from sqlalchemy import Table, Column, ForeignKey, Integer, String, MetaData, func, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


class GroupSends(Base):
    __tablename__ = 'groupsends'

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_name: Mapped[str]
    # count_inside_buckets: Mapped[int] = mapped_column(default=0)
    # create_at = Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class RequestsNames(Base):
    __tablename__ = 'requests_number'

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_id: Mapped[int] = mapped_column(ForeignKey("groupsends.id", ondelete="CASCADE"))




class InboxFiles(Base):
    __tablename__ = 'inboxfiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    send_number_id: Mapped[int] = mapped_column(ForeignKey("requests_number.id", ondelete="CASCADE"))


engine = create_engine('sqlite:///test-sqlite3.db')
# Base.metadata.create_all(engine)
