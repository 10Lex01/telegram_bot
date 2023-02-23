from sqlalchemy import Column, Integer, String, Date
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True)
    balance = Column(Integer)
    date_expiration = Column(Date)
    description = Column(String, nullable=True)

    def __repr__(self):
        return f'{self.id}. {self.user_name}'
