import os
from dotenv import load_dotenv
import pytest
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.main import app
from app.core.config import settings
from app.models.base import Base
from app.core.database import get_db

load_dotenv()

# Test database
test_engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True
)
TestingSessionLocal = sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.rollback()
        
        await connection.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    # Override the get_db dependency to use test database
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(base_url=os.getenv("BASE_URL")) as client:
        yield client
    
    # Clear the override
    app.dependency_overrides.clear()