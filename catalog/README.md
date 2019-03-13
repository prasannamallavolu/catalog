# Item-Catalogue
created by
## Prasanna Mallavolu
# About the project
This contains the diiferent company refrigerators.Each company has several fridge models.Either company name or fridge model an be edited or deleted when the user is login through the gmail.This contains mainly the CRUD operations on items
# Files
1) database.py - contains the database tables and their attributes
2) insertingt.py - contains the dummy data for the tables
3) main.py  - main python file to run the application
4) templates  - contains the html pages
5) static - contains css and java script files
6) refrigarators.db  - database of refrigarators
7) images - contains the output screens of project

# Requirements
  [Vagrant](https://www.vagrantup.com/)
  [Udacity Vagrantfile](https://github.com/udacity/fullstack-nanodegree-vm)
  [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
  [python](https://www.python.org/downloads/)

# Enivironment
It needs VM to run this project -- that way any changes that you make won't affect your personal machine setup.

1) Install Vagrant and Virtualbox.
2) In the vagrant file (https://github.com/udacity/fullstack-nanodegree-vm) place this downloaded zip file of fridges(python/fridges).
3) Launch the Vagrant VM by using vagrant up in the directory.
4) Sign into the VM by using vagrant ssh in the directory.
5) This application needs dependency modules which are not present in the VM. so we need to install them by using
    pip install flask - for installing flask module
    pip install sqlalchemy  - for installing sqlalchemy module
    pip install oauth2client  - for installing oauth2client module
    pip install psycopg2  - for installing psycop2
    pip install requests  - for installing requests
6) To end the connection to the VM type exit.
7) To shut down the VM while still saving your work, type vagrant halt.
# How to Run
run the python file database.py by using python database.py
run the python file inserting.py by using python inserting.py
run the main python file by using python main.py
visit the google chrome and enter http://localhost:8000
# JSON endpoints
http://localhost:8000/refrigarators/JSON  - displays all the fridge companies and the fridges
http://localhost:8000/refrigarators/fridgeCompanies/JSON  - displays all fridge companies
http://localhost:8000/refrigarators/fridges/JSON  - displays all fridges
http://localhost:8000/refrigarators/<path:fridge_name>/fridges/JSON  - displays specific company fridges
http://localhost:8000/refrigarators/<path:fridge_name>/<path:edition_name>/JSON - display specific fridge of specific company

NOTE: Gmail signin takes few minutes to login.
