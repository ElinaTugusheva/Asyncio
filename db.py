import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column
from sqlalchemy import INTEGER, JSON, String

POSTGRES_USER = os.getenv('POSTGRES_USER','swapi')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD','secret')
POSTGRES_DB = os.getenv('POSTGRES_DB','swapi')
POSTGRES_HOST = os.getenv('POSTGRES_HOST','localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT','5432')

PG_DSN = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

engine = create_async_engine(PG_DSN, echo=True)
DbSession = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):
    __tablename__ = 'swapi'
    id: MappedColumn[int] = mapped_column(INTEGER, primary_key=True)
    name: MappedColumn[str] = mapped_column(String(100), nullable=False)
    birth_year: MappedColumn[str] = mapped_column(String(20), nullable=True)
    eye_color: MappedColumn[str] = mapped_column(String(50), nullable=True)
    gender: MappedColumn[str] = mapped_column(String(20), nullable=True)
    hair_color: MappedColumn[str] = mapped_column(String(50), nullable=True)
    homeworld: MappedColumn[str] = mapped_column(String(255), nullable=True)
    mass: MappedColumn[str] = mapped_column(String(20), nullable=True)
    skin_color: MappedColumn[str] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<SwapiPeople(id={self.id}, name='{self.name}')>"

async def open_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы!")


async def close_orm():
    await engine.dispose()