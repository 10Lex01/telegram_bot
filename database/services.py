import datetime
from typing import Dict
from dateutil.relativedelta import relativedelta
from . import tables
from .database import Session


def add_to_db_users(data: Dict, transfer_date: str) -> None:
    with Session() as session:
        user = tables.User(**data)
        session.add(user)
        session.commit()
        create_operation(user_id=user.id, summ=data['balance'], transfer_date=transfer_date)


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
        if user.date_expiration < datetime.datetime.now().date():
            user.date_expiration = datetime.datetime.now().date() + relativedelta(months=int(balance)//100)
        else:
            user.date_expiration += relativedelta(months=int(balance)//100)
        session.commit()


def delete_user_from_db(user_name):
    with Session() as session:
        session.query(tables.User).filter_by(user_name=user_name).delete()
        session.commit()


def create_operation(summ, transfer_date, user_id=None, user_name=None):
    with Session() as session:
        date_operation = datetime.datetime.strptime(transfer_date, "%d.%m.%Y").date()
        if user_id:
            operation = tables.Operation(user_id=user_id, date_operation=date_operation, summ=int(summ))
        elif user_name:
            id_user = session.query(tables.User).filter_by(user_name=user_name).first().id
            operation = tables.Operation(user_id=id_user, date_operation=date_operation, summ=int(summ))
        session.add(operation)
        session.commit()


def get_all_operations_from_db():
    with Session() as session:
        user_operations = session.query(tables.Operation).all()
    return user_operations


def get_user_operations_from_db(user_id, limit=None):
    with Session() as session:
        if limit:
            user_operations = session.query(tables.Operation).filter_by(user_id=user_id).order_by(tables.Operation.date_operation.desc()).limit(limit)
        else:
            user_operations = session.query(tables.Operation).filter_by(user_id=user_id).order_by(tables.Operation.date_operation.desc()).limit(5)
    return user_operations
