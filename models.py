from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from  sqlalchemy.orm import relationship
from sqlalchemy import create_engine

engine = create_engine('sqlite:///test-sqlite3.db')

Base = declarative_base()

Base.metadata.create_all(engine)

class GroupSends(Base):
    __tablename__ = 'groupsends'

    id = Column(Integer, primary_key=True)
    send_number = Column(Integer, nullable=False)
    bucket_name = Column(String(250), nullable=False)
    inbox_file = relationship('InboxFiles', cascade="all,delete")

class InboxFiles(Base):
    __tablename__ = 'inboxfiles'

    id = Column(Integer, primary_key=True)
    req_send = Column(Integer, nullable=False)
    file_name = Column(String(250), nullable=False)
    send_number_id = Column(Integer, ForeignKey('groupsends.id'))
    send_number = relationship("GroupSends")

# with engine.connect() as conn:
#     conn.execute('SELECT VER')