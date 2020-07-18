import sqlalchemy
from .db_session import SqlAlchemyBase


class Date(SqlAlchemyBase):
    __tablename__ = 'dates'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    day = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    month = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    epoch = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    importance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return "id: {}\nDate: {}:{}:{}\nDescription: {}\nImportance: {}".format(self.id, self.day, self.month, self.year, self.description, self.importance)
