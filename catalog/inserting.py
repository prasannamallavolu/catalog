from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database import *

engine = create_engine('sqlite:///refrigarators.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
session.query(P_CompName).delete()
session.query(P_FridgeName).delete()
session.query(User).delete()
User_Prasanna = User(
    name="Prasanna",
    email="prasannamallavolu@gmail.com",
    picture="/")
session.add(User_Prasanna)
session.commit()
print('The user is successfully added!!!')
# creating company names
p_comp1 = P_CompName(p_name="SAMSUNG", user_id=1)
session.add(p_comp1)
session.commit()
p_comp2 = P_CompName(p_name="LG", user_id=1)
session.add(p_comp2)
session.commit()
p_comp3 = P_CompName(p_name="GODREJ", user_id=1)
session.add(p_comp3)
session.commit()
p_comp4 = P_CompName(p_name="PANASONIC", user_id=1)
session.add(p_comp4)
session.commit()
# creating subjects
p_fridge1 = P_FridgeName(
    f_name='SAMSUNG',
    f_color='purple',
    f_capacity='230L',
    f_doors='2',
    f_doorlock='Yes',
    f_price='30,000',
    f_starrating='4',
    f_date=datetime.datetime.now(),
    compnameid=1,
    user_id=1)
session.add(p_fridge1)
session.commit()
p_fridge2 = P_FridgeName(
    f_name='LG',
    f_color='BLUE',
    f_capacity='250L',
    f_doors='3',
    f_doorlock='Yes',
    f_price='40,000',
    f_starrating='5',
    f_date=datetime.datetime.now(),
    compnameid=2,
    user_id=1)
session.add(p_fridge2)
session.commit()
p_fridge3 = P_FridgeName(
    f_name='GODREJ',
    f_color='Black',
    f_capacity='1400L',
    f_doors='1',
    f_doorlock='No',
    f_price='15,000',
    f_starrating='2',
    f_date=datetime.datetime.now(),
    compnameid=3,
    user_id=1)
session.add(p_fridge3)
session.commit()
p_fridge4 = P_FridgeName(
    f_name='PANASONIC',
    f_color='purple',
    f_capacity='230L',
    f_doors='2',
    f_doorlock='Yes',
    f_price='30,000',
    f_starrating='4',
    f_date=datetime.datetime.now(),
    compnameid=4,
    user_id=1)
session.add(p_fridge4)
session.commit()
print("Subjects are added succesfully")
