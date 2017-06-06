from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response
from flask import g

from functools import wraps

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Categories, Items

import random
import string
import httplib2
import json
import requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ITEM CATALOG"

@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE = state)

engine = create_engine('sqlite:///itemCatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# JSON API Endpoints

@app.route("/genre/<int:category_id>/games/json")
def genreGamesJSON(category_id):
	genre = session.query(Categories).filter_by(id = category_id).one()
	games = session.query(Items).filter_by(category_id = category_id).all()
	return jsonify(Games = [i.serialize for i in games])

@app.route("/catalog/json/")
def genreJSON():
	genres = session.query(Categories).all()
	return jsonify(genres = [g.serialize for g in genres])

@app.route("/genre/<int:category_id>/games/<int:item_id>/json")
def gameDescriptionJSON(category_id, item_id):
	items = session.query(Items).filter_by(id = item_id).one()
	return jsonify(gameDescription = items.serialize)

# Display current list of genres (READ)

@app.route('/')
@app.route('/catalog/')
def showCatalog():
	catalog = session.query(Categories).order_by(asc(Categories.name))
	games = session.query(Items).order_by(desc(Items.id)).limit(10)
	if 'username' not in login_session:
		return render_template('publiccatalog.html',
					categories = catalog, games = games
		)
	else:
		currentUser = getUserInfo(login_session['user_id'])
	 	return render_template('catalog.html',
					categories = catalog, currentUser = currentUser, games = games
		)

# Add a new genre (CREATE)

@app.route('/genre/add/', methods=['GET', 'POST'])
def addGenre():
	if 'username' not in login_session:
		flash("You are not logged in.")
		return redirect('/login')
	if request.method == "POST":
		currentUser = getUserInfo(login_session['user_id'])
		newGenre = Categories(
			name = request.form['name'], user_id = login_session['user_id'])
		session.add(newGenre)
		flash("You've added a new genre: %s" % newGenre.name)
		session.commit()
		return redirect(url_for('showCatalog'))
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template('newGenre.html', currentUser = currentUser)

# Delete Genre (DELETE)

@app.route('/genre/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(category_id):
	if 'username' not in login_session:
		flash("You are not logged in.")
		return redirect('/login')
	toDelete = session.query(Categories).filter_by(id=category_id).one()
	if toDelete.user_id != login_session['user_id']:
		flash("You can't delete genres you didn't create.")
		return redirect(url_for('showCatalog'))
	if request.method == "POST":
		session.delete(toDelete)
		flash("You have deleted: %s!" % (toDelete.name))
		session.commit()
		return redirect(url_for("showCatalog", category_id = category_id))
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template('deleteGenre.html', genre = toDelete, currentUser = currentUser)

# Edit Genre (UPDATE)

@app.route('/genre/<int:category_id>/edit/', methods=["GET", "POST"])
def editGenre(category_id):
	if 'username' not in login_session:
		flash("You are not logged in.")
		return redirect('/login')
	toEdit = session.query(Categories).filter_by(id = category_id).one()
	if toEdit.user_id != login_session['user_id']:
		flash("You can't edit genres you didn't create.")
		return redirect(url_for('showCatalog'))
	if request.method == "POST":
		toEdit.name = request.form['name']
		flash("Genre succesfully updated: %s" % (toEdit.name))
		return redirect(url_for('showCatalog'))
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template("editGenre.html", genre = toEdit, currentUser = currentUser)

# Show list of games in a genre (READ)

@app.route('/genre/<int:category_id>/games/')
def showGames(category_id):
	genre = session.query(Categories).filter_by(id = category_id).one()
	creator = getUserInfo(genre.user_id)
	items = session.query(Items).filter_by(category_id = category_id).all()
	if 'username' not in login_session:
		return render_template('publicgames.html', items = items, genre = genre, creator = creator)
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template('games.html', items = items, genre = genre, creator = creator, currentUser = currentUser)


# Add game into genre (CREATE)

@app.route('/genre/<int:category_id>/games/add/', methods=['GET', 'POST'])
def addGames(category_id):
	if 'username' not in login_session:
		flash("You are not logged in.")
		return redirect('/login')
	currentCategory = session.query(Categories).filter_by(id = category_id).one()
	if login_session['user_id'] != currentCategory.user_id:
		flash("You can't add games in a genre you didn't create.")
		return redirect(url_for('showCatalog'))
	if request.method == "POST":
		newGame = Items(name = request.form['name'], description = request.form['description'],
			category_id = category_id)
		session.add(newGame)
		flash("You have added a new game: %s" % (newGame.name))
		session.commit()
		return redirect(url_for('showGames', category_id = category_id))
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template("addGame.html", genre = currentCategory, currentUser = currentUser)

# Edit existing game in genre (UPDATE)

@app.route('/genre/<int:category_id>/games/<int:item_id>/edit/', methods=["GET", "POST"])
def editGames(item_id, category_id):
	if 'username' not in login_session:
		return redirect('/login')
	toEdit = session.query(Items).filter_by(id = item_id).one()
	currentCategory = session.query(Categories).filter_by(id = category_id).one()
	if login_session['user_id'] != currentCategory.user_id:
		flash("You can't edit games you didn't create.")
		return redirect(url_for('showCatalog'))
	if request.method == "POST":
		if request.form['name']:
			toEdit.name = request.form['name']
		if request.form['description']:
			toEdit.description = request.form['description']
		session.add(toEdit)
		flash("Game info successfully updated: %s" % (toEdit.name))
		session.commit()
		#TODO: Catch error and flash diff message
		return redirect(url_for("showDescription", category_id = category_id, item_id = item_id))
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template("editGame.html", gameItem = toEdit, category_id = currentCategory, currentUser = currentUser)

# Delete existing game (DELETE)

@app.route('/genre/<int:category_id>/games/<int:item_id>/delete/', methods = ['GET', 'POST'])
def deleteGames(item_id, category_id):
	if 'username' not in login_session:
		flash("You are not logged in.")
		return redirect('/login')
	toDelete = session.query(Items).filter_by(id = item_id).one()
	currentCategory = session.query(Categories).filter_by(id = category_id).one()
	if login_session['user_id'] != currentCategory.user_id:
		flash("You can't delete games you didn't create.")
		return redirect(url_for('showCatalog'))
	if request.method == "POST":
		session.delete(toDelete)
		flash("You have deleted this game: %s" % (toDelete.name))
		session.commit()
		return redirect(url_for('showGames', category_id = category_id))
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template("deleteGame.html", gameItem = toDelete, category_id = currentCategory, currentUser = currentUser)

# Show description of a game (READ)

@app.route('/genre/<int:category_id>/games/<int:item_id>/')
def showDescription(item_id, category_id):
	game = session.query(Items).filter_by(id = item_id).one()
	currentCategory = session.query(Categories).filter_by(id = category_id).one()
	#TODO: add usercheck
	if 'username' not in login_session:
		return render_template('publicgameInfo.html', game = game, category = currentCategory)
	else:
		currentUser = getUserInfo(login_session['user_id'])
		return render_template('gameInfo.html', game = game, category = currentCategory, currentUser = currentUser)

# Google Connect OAuth

@app.route('/gconnect', methods = ['POST'])
def gconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state!'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	code = request.data

	try:
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application.json'
		return response

	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token user ID does not match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token client's ID does not match the app's ID."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps("Current user already connected."), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token,'alt':'json'}
	answer = requests.get(userinfo_url, params=params)
	data = answer.json()
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']
	# ADD PROVIDER TO LOGIN SESSION
	login_session['provider'] = 'google'
	# see if user exists, if it doesn't make a new one
	user_id = getUserID(data["email"])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id
	flash("You are now logged in as %s" % login_session['username'])
	return redirect(url_for("success"))


@app.route('/login/success')
def success():
	return render_template('success.html', login_session = login_session)
	
# Google Connect disconnect
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Log out

@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))

# User functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

if __name__ == '__main__':
	app.secret_key = "udacityFullStack"
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
