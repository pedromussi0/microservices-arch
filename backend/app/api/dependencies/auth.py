from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserLogin
from app.services.auth_service import AuthService
from app.services.token_service import TokenService
from app.services.user_service import UserService


def get_user_service() -> UserService:
    return UserService()


def get_token_service() -> TokenService:
    return TokenService()


def get_auth_service(
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
) -> AuthService:
    return AuthService(user_service, token_service)
