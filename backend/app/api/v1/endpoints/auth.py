from datetime import timedelta
from typing import Dict
from fastapi import APIRouter, Body, Depends, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.auth_service import AuthHandler
from app.core.exceptions import AuthenticationException, DuplicateEntityException, RegistrationException

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    try:
        db_user = await AuthHandler.register_user(db, user)
        return db_user
    except DuplicateEntityException as e:
        raise HTTPException(status_code=400, detail=str(e.detail))
    except RegistrationException as e:
        raise HTTPException(status_code=500, detail=str(e.detail))
    
@router.post("/token")
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Authenticate user
        user = await AuthHandler.authenticate_user(db, login_data)
       
        # Create access and refresh tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=7)
        
        access_token = AuthHandler.create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        refresh_token = AuthHandler.create_refresh_token(
            data={"sub": user.email},
            expires_delta=refresh_token_expires
        )
       
        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
   
    except AuthenticationException as e:
        raise HTTPException(status_code=401, detail=str(e.detail))

@router.post("/refresh-token")
async def refresh_token(
    token_data: Dict[str, str] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Extract refresh token from the dictionary
        refresh_token = token_data.get('refresh_token')
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token is required")
        
        # Refresh tokens
        tokens = await AuthHandler.refresh_tokens(db, refresh_token)
        return tokens
    
    except AuthenticationException as e:
        raise HTTPException(status_code=401, detail=str(e.detail))
    
@router.post("/validate-token")
async def validate_token(
    token_data: Dict[str, str] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        access_token = token_data.get('access_token')
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")
        
        user_details = await AuthHandler.validate_access_token(db, access_token)
        
        return {
            "valid": True, 
            **user_details
        }
    
    except AuthenticationException as e:
        raise HTTPException(status_code=401, detail=str(e.detail))