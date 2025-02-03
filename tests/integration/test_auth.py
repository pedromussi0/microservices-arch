import pytest
from httpx import AsyncClient
import random

@pytest.mark.asyncio
async def test_user_registration(client: AsyncClient):
    random_email = f"test{random.randint(1000, 9999)}@example.com"
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": random_email,
            "password": "strongpassword123",
            "full_name": "Test User3"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == random_email
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_duplicate_email_registration(client: AsyncClient):
    # First registration
    duplicate_email = f"duplicate{random.randint(1000, 9999)}@example.com"
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": duplicate_email,
            "password": "strongpassword123",
            "full_name": "1stemailuser"
        }
    )
    
    # Second registration with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": duplicate_email,
            "password": "anotherpassword456",
            "full_name": "2ndemailuser"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]