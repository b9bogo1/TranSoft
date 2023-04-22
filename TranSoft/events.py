from sqlalchemy import DateTime, event
from sqlalchemy.orm import mapper # import mapper from sqlalchemy.orm
from sqlalchemy.orm import class_mapper # import class_mapper from sqlalchemy.orm
from TranSoft.models import User, Reading
from TranSoft import db

READING_MAX_DATA = 691199
USER_MAX_DATA = 5

@event.listens_for(User, "before_insert")
def delete_oldest_entries(mapper, connection, target):
    max_entries = USER_MAX_DATA # change this as needed
    current_count = connection.scalar(db.select(db.func.count(User.id)))
    if current_count > max_entries:
        # get the ids of the oldest entries to delete
        oldest_ids = connection.execute(
            User.__table__.select().order_by(User.created_at.asc()).limit(current_count - max_entries)
        ).fetchall()
        # convert the list of tuples to a list of ids
        oldest_ids = [row[0] for row in oldest_ids]
        # delete the oldest entries by ids
        connection.execute(
            User.__table__.delete().where(User.id.in_(oldest_ids))
        )
        print(current_count)
        print(connection.scalar(db.select(db.func.count(User.id))))


@event.listens_for(Reading, "before_insert")
def delete_oldest_entries(mapper, connection, target):
    max_entries = READING_MAX_DATA # change this as needed
    current_count = connection.scalar(db.select(db.func.count(Reading.id)))
    if current_count > max_entries:
        # get the ids of the oldest entries to delete
        oldest_ids = connection.execute(
            Reading.__table__.select().order_by(Reading.created_at.asc()).limit(current_count - max_entries)
        ).fetchall()
        # convert the list of tuples to a list of ids
        oldest_ids = [row[0] for row in oldest_ids]
        # delete the oldest entries by ids
        connection.execute(
            Reading.__table__.delete().where(Reading.id.in_(oldest_ids))
        )
        print(current_count)
        print(connection.scalar(db.select(db.func.count(Reading.id))))
