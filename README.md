# Item Catalog

Full Stack Nanodegree Program Project #5. Tasked with creating an item catalog using Flask and SQLAlchemy. Language in this project was Python 2.7.

## Getting Started

Clone this repository by typing `git clone https://github.com/bryancresswell/itemCatalog.git`

## Launching Vagrant

Once you have installed [Vagrant](vagrantup.com), clone the Full Stack Nanodegree files from [here](https://github.com/udacity/fullstack-nanodegree-vm). Once done, navigate to the folder, then type `vagrant up`. Once ready, type `vagrant ssh` which will connect you to the VM.

## Setting up the database

Once you are connected in the VM, type `cd /vagrant` to change to the current directory. Navigate to `/catalog`. You should see `vagrant@vagrant-ubuntu-trusty-32:/vagrant/catalog$`. This will be where you enter your commands. To set up the database, first type `python database_setup.py`. This is to create the schema. You should see a `itemCatalog.db` file after you type that command. Next, type `python testData.py`. This is to populate the database with some sample data.

## Testing

Once the database is created, you are all ready to test the app! To test, type `python main.py`. Once ready, type `localhost:5000/` in your browser. When you have loaded the website, create an account by pressing the `Login` button, or feel free to browse around.

## Lessons Learnt

I am getting more familiar with Flask as we go through this project. Also, I now have a better understanding of relationships between tables as well as how to efficiently use popular libraries and ORMs such as SQLAlchemy. One of the challenges was the debugging phase, which required me to catch a lot of edge cases. This was a fun project to undertake in general.
