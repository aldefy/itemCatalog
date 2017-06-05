from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Categories, Items

engine = create_engine("sqlite:///itemCatalog.db")

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

session = DBSession()

# Create users

User1 = User(name = "John Wick", email = "johnwick@gmail.com",
		picture = "http://cdn.bloody-disgusting.com/wp-content/uploads/2015/03/John-Wick-Keanu-Reeves2.jpg")

session.add(User1)
session.commit()

User2 = User(name = "Wonder Woman", email = "wonderwoman@gmail.com",
		picture = "http://www.cosmicbooknews.com/sites/default/files/galww2.png")

session.add(User2)
session.commit()

# Category "First Person Shooters"

category1 = Categories(user_id=1, name = 'First Person Shooters')

session.add(category1)
session.commit()

# "First Person Shooters"

item1 = Items(user_id = 1, name = "Far Cry 4", description = """Far Cry 4 is a
		first-person action-adventure game. Players assume control 
		of Ajay Ghale, 
		a Kyrati-American who is on a quest to spread his
		deceased mother's ashes in the fictional country of Kyrat.""",
		category = category1
	)

session.add(item1)
session.commit()

item2 = Items(user_id = 1, name = "Counter Strike", description = """
		Counter Strike is a first-person action-adventure game.
		Players choose from the Terrorists or Counter Terrorists
		and work to achieve their faction's goals.""",
		category = category1
	)

session.add(item2)
session.commit()

# Category "Third Person Shooters"

category2 = Categories(user_id=1, name = 'Third Person Shooters')
 
session.add(category2)
session.commit()

# "Third Person Shooters"

item1 = Items(user_id = 1, name = "Grand Theft Auto 5", description = """Grand Theft Auto V
		is a third-person action-adventure game. Players assume control 
                of 3 characters, in a bid to become the ruler of Los Santos.""",
                category = category2
        )

session.add(item1)
session.commit()

item2 = Items(user_id = 1, name = "PlayerUnknown's Battlegrounds", description = """
                PlayerUnknown's Battlegrounds is a third person survival game.
                Players go up against 99 other players to be the last man standing.""",
                category = category2
        )

session.add(item2)
session.commit()

print "Added Menu Items"
