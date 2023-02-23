from typing import Dict, List, Union
from sqlalchemy.orm import Session as Sa_session, joinedload
from . import tables
from .database import Session


def add_to_database(data: Dict) -> None:
    with Session() as session:
        user = tables.User(**data)
        session.add(user)
        session.commit()

