from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthHandler
from app.core.exceptions import DuplicateEntityException, RegistrationException

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