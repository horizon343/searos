from sqlalchemy import Column, Integer, String
from db.models.base_model import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
