from sqlalchemy import Column, Integer, String, Date, ForeignKey
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    balance = Column(Integer)
    date_expiration = Column(Date)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f'{self.id}. {self.user_name}'


class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    summ = Column(Integer)
    date_operation = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return f'{self.user_id}'
