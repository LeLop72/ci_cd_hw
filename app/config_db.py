from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative.api import DeclarativeMeta
DATABASE_URL = "sqlite+aiosqlite:///./recipe.db"

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False,
                             class_=AsyncSession)
local_session = async_session()
Base: DeclarativeMeta = declarative_base()
