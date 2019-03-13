import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine


# to create database
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    picture = Column(String(200))


class P_CompName(Base):
    __tablename__ = 'compname'
    id = Column(Integer, primary_key=True)
    p_name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    p_user = relationship(User, backref="compname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'p_name': self.p_name,
            'id': self.id
        }


class P_FridgeName(Base):
    __tablename__ = 'fridgename'
    f_name = Column(String(200), nullable=False)
    id = Column(Integer, primary_key=True)
    f_color = Column(String(150))
    f_capacity = Column(String(150))
    f_doors = Column(Integer)
    f_doorlock = Column(String(50))
    f_price = Column(Integer)
    f_starrating = Column(Integer)
    f_date = Column(DateTime, nullable=False)
    compnameid = Column(Integer, ForeignKey('compname.id'))
    compname = relationship(
        P_CompName, backref=backref('fridgename', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="fridgename")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'f_name': self.f_name,
            'f_color': self.f_color,
            'f_capacity': self.f_capacity,
            'f_doors': self.f_doors,
            'f_doorlock': self.f_doorlock,
            'f_price': self.f_price,
            'f_date': self.f_date,
            'id': self. id
        }

engin = create_engine('sqlite:///refrigarators.db')
Base.metadata.create_all(engin)
