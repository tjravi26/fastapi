from .database import Base
from sqlalchemy import Column, Integer, String


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, nullable=False)
    person = Column(String, nullable=False)
    content = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
