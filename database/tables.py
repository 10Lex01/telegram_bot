from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True)
    balance = Column(Integer)
    date_expiration = Column(Date)
    description = Column(String, nullable=True)
    operations = relationship('Operation', backref='user')

    def __repr__(self):
        return f'{self.id}. {self.user_name}'


class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    summ = Column(Integer)
    date_operation = Column(Date)
    user_id = Column(Integer, ForeignKey('users.id'))
