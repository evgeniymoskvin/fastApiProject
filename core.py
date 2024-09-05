# from models import metadate_obj
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base


engine = create_engine('sqlite:///test-sqlite3.db')

session = sessionmaker(engine)
session2 = Session(engine)
session1 = engine.begin()

def create_tables():
    Base.metadata.create_all(engine)
    # metadate_obj.drop_all(engine)
    # metadate_obj.create_all(engine)


