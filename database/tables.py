from sqlalchemy import Column, Integer, String, Date
from database.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_name = Column(String, unique=True)
    balance = Column(Integer)
    date_expiration = Column(Date)

    def __repr__(self):
        return f"User(id={self.id!r}, " \
               f"user_name={self.user_name!r}, " \
               f"balance={self.balance!r}, " \
               f"transfer_date={self.date_expiration!r})"
