from typing import Dict
from dateutil.relativedelta import relativedelta
from . import tables
from .database import Session


def add_to_db_users(data: Dict) -> None:
    with Session() as session:
        user = tables.User(**data)
        session.add(user)
        session.commit()


def get_all_users_from_db():
    with Session() as session:
        users = session.query(tables.User).all()
    return users


def get_user_balance_from_db(user_name):
    with Session() as session:
        user = session.query(tables.User).filter_by(user_name=user_name).first()
    return user


def update_balance_and_date_for_user(user_name, balance):
    with Session() as session:
        user = session.query(tables.User).filter_by(user_name=user_name).first()
        user.balance += int(balance)
        user.date_expiration += relativedelta(months=int(balance)//100)
        session.commit()


def delete_user_from_db(user_name):
    with Session() as session:
        session.query(tables.User).filter_by(user_name=user_name).delete()
        session.commit()
