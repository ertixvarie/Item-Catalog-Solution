from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    picture = Column(String)


class Job(Base):
    __tablename__ = 'job'

    name = Column(String(250), primary_key=True)

    @property
    def serialize(self):
        return {
            'name': self.name,
        }


class Weapon(Base):
    __tablename__ = "weapon"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable = False)
    level = Column(Integer)
    job_req = Column(String(250), ForeignKey('job.name'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'job_req': self.job_req
        }



engine = create_engine('sqlite:///armory.db')

Base.metadata.create_all(engine)
