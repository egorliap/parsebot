from scr.database.config import settings

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    echo=True
)

session_factory = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass