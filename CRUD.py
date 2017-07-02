from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Job, Weapon


#class Operators:

def makeSession():
    engine = create_engine('sqlite:///armory.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind = engine)
    session = DBSession()
    return session

def getJobs(session):
    return session.query(Job).all()


def getWeapons(session):
    return session.query(Weapon)


def addEntry(session, data):
    session.add(data)
    session.commit()


def deleteEntry(session, data):
    session.delete(data)
    session.commit()