from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Job, Weapons
from CRUD import makeSession, getJobs

session = makeSession()
display = getJobs(session)
print display
