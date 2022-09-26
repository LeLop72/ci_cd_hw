from sqlalchemy import Column, Integer, String

from app.config_db import Base


class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    time_in_minutes = Column(Integer)
    description = Column(String)
    counter = Column(Integer, server_default="0")
    ingredients = Column(String)
