from data.db_session import create_session
from data.dates import Date


def get_events(day, month):
    session = create_session()
    return session.query(Date).filter(Date.day == day, Date.month == month)


def set_importance_event(id_date, value):
    session = create_session()
    date = session.query(Date).filter(Date.id == id_date)
    date.importance = value
    session.commit()