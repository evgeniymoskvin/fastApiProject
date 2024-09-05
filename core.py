# from models import metadate_obj
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


engine = create_engine('sqlite:///test-sqlite3.db', echo=True)

session = sessionmaker(engine)

session1 = engine.begin()
def create_tables():
    Base.metadata.create_all(engine)
    # metadate_obj.drop_all(engine)
    # metadate_obj.create_all(engine)


