from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GroupSends(Base):
    __tablename__ = 'groupsends'

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_name: Mapped[str]

    # relationships
    request_numbers = relationship('RequestsNames', backref='group_send', cascade='all, delete')

    def __str__(self):
        return f'{self.__class__.__name__} | bucket_name = {self.bucket_name}'


class RequestsNames(Base):
    __tablename__ = 'requests_number'

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_id: Mapped[int] = mapped_column(ForeignKey("groupsends.id", ondelete="CASCADE"))

    # relationships
    inbox_files = relationship('InboxFiles', backref='requests_number', cascade='all, delete')

    # def __str__(self):
    #     return f'{self.__class__.__name__} | req_id = {self.id} : {self.bucket_id}'

class InboxFiles(Base):
    __tablename__ = 'inboxfiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    send_number_id: Mapped[int] = mapped_column(ForeignKey("requests_number.id", ondelete="CASCADE"))


engine = create_engine('sqlite:///test-sqlite3.db')
engine_async = create_async_engine('sqlite+aiosqlite:///test-sqlite3.db')

# Base.metadata.create_all(engine)
