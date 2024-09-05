from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, ForeignKey, Integer, String, MetaData, func, DateTime
from  sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

class GroupSends(Base):
    __tablename__ = 'groupsends'

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_name: Mapped[str]
    count_inside_buckets: Mapped[int] = mapped_column(default=0)
    # create_at = Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class InboxFiles(Base):
    __tablename__ = 'inboxfiles'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str]
    send_number_id: Mapped[int] = mapped_column(ForeignKey("groupsends.id", ondelete="CASCADE"))



# groupsends = Table(
#     'groupsends',
#     metadate_obj,
#     Column('id', Integer, primary_key=True),
#     Column('bucket_name', String)


# with engine.connect() as conn:
#     conn.execute('SELECT VER')