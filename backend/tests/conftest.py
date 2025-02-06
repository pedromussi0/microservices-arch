import asyncio
from typing import AsyncGenerator
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.main import app

async_engine = create_async_engine(
    settings.TEST_DATABASE_URL, 
    echo=settings.DEBUG,
    future=True
)

AsyncSessionLocal = sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")

@pytest.fixture(scope="session")
async def db_session(event_loop) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
async def client(event_loop, db_session: AsyncSession):
    async with AsyncClient(transport=ASGITransport(app=app),base_url="http://testserver") as client:
        yield client
