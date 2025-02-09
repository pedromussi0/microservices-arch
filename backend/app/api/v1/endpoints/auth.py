# app/api/v1/endpoints/auth.py
from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import (
    get_auth_service,
    get_token_service,
    get_user_service,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import (
    AuthenticationException,
    DuplicateEntityException,
    RegistrationException,
)
from app.core.logger import logger
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
):
    """
    Register a new user.
    """
    try:
        logger.info(f"Attempting to register user: {user.email}")
        db_user = await user_service.register_user(db, user)
        logger.info(f"Successfully registered user: {user.email}")
        return db_user
    except DuplicateEntityException as e:
        logger.warning(f"Registration failed - duplicate user: {user.email}")
        raise HTTPException(status_code=400, detail=str(e.detail))
    except RegistrationException as e:
        logger.error(f"Registration failed - server error: {str(e.detail)}")
        raise HTTPException(status_code=500, detail=str(e.detail))


@router.post("/token")
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Authenticate user and return tokens.
    """
    try:
        logger.info(f"Login attempt for user: {login_data.email}")
        user = await auth_service.authenticate_user(db, login_data)

        access_token = auth_service.token_service.create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        refresh_token = auth_service.token_service.create_refresh_token(
            data={"sub": user.email}, expires_delta=timedelta(days=7)
        )

        logger.info(f"Login successful for user: {login_data.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except AuthenticationException as e:
        logger.warning(f"Login failed for user {login_data.email}: {str(e.detail)}")
        raise HTTPException(status_code=401, detail=str(e.detail))


@router.post("/refresh-token")
async def refresh_token(
    token_data: Dict[str, str] = Body(...),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Refresh access and refresh tokens.
    """
    try:
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            logger.warning("Refresh token attempt without token")
            raise HTTPException(status_code=400, detail="Refresh token is required")

        logger.info("Attempting to refresh tokens")
        tokens = await auth_service.refresh_tokens(db, refresh_token)
        logger.info("Tokens refreshed successfully")
        return tokens

    except AuthenticationException as e:
        logger.warning(f"Token refresh failed: {str(e.detail)}")
        raise HTTPException(status_code=401, detail=str(e.detail))


@router.post("/validate-token")
async def validate_token(
    token_data: Dict[str, str] = Body(...),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Validate access token and return user details.
    """
    try:
        access_token = token_data.get("access_token")
        if not access_token:
            logger.warning("Token validation attempt without token")
            raise HTTPException(status_code=400, detail="Access token is required")

        logger.info("Validating access token")
        user_details = await auth_service.validate_access_token(db, access_token)
        logger.info(f"Token validated successfully for user: {user_details['email']}")

        return {"valid": True, **user_details}

    except AuthenticationException as e:
        logger.warning(f"Token validation failed: {str(e.detail)}")
        raise HTTPException(status_code=401, detail=str(e.detail))


# Optional: Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint for the auth service.
    """
    return {
        "status": "healthy",
        "service": "auth",
        # "version": settings.API_VERSION
    }
