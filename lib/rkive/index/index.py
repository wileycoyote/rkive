from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine

association_table = Table('association', Base.metadata,
    Column('opus_id', Integer, ForeignKey('opus.id')),
    Column('participant_id', Integer, ForeignKey('participant.id'))
)

class Opus(Base):
    __tablename__ = 'opus'
    id = Column(Integer, primary_key=True)
    participant = relationship("Participant",
                    secondary=association_table)
    category = Column(String)
    children = relationship("Media")

class Participant(Base):
    __tablename__ = 'participant'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    role = Column(String)

class Media(Base):
    __tablename__= 'media'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('opus.id'))
    media = Column(String)
    year_recorded = Column(String)
    year_reissued = Column(String)

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('postgresql://postgres:postgres@192.168.1.155/MediaIndex')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
db = DBSession()    
    
