from datetime import timedelta
from typing import Dict

from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.core.logger import logger
from app.interfaces.auth import IAuthService, ITokenService, IUserService
from app.models.user import User
from app.schemas.user import UserLogin


class AuthService(IAuthService):
    def __init__(self, user_service: IUserService, token_service: ITokenService):
        self.user_service = user_service
        self.token_service = token_service

    async def authenticate_user(self, db, login_data: UserLogin) -> User:
        user = await self.user_service.get_user_by_email(db, login_data.email)

        if not user:
            logger.warning(
                f"Authentication failed - user not found: {login_data.email}"
            )
            raise AuthenticationException(detail="Incorrect email or password")

        if not await self.user_service.verify_password(
            login_data.password, user.hashed_password
        ):
            logger.warning(
                f"Authentication failed - invalid password: {login_data.email}"
            )
            raise AuthenticationException(detail="Incorrect email or password")

        if not user.is_active:
            logger.warning(f"Authentication failed - inactive user: {login_data.email}")
            raise AuthenticationException(detail="User account is not active")

        logger.info(f"User authenticated successfully: {login_data.email}")
        return user

    async def validate_access_token(self, db, access_token: str) -> Dict:
        payload = self.token_service.verify_token(access_token, token_type="access")
        user = await self.user_service.get_user_by_email(db, payload.get("sub"))

        if not user:
            logger.warning(
                f"Token validation failed - user not found: {payload.get('sub')}"
            )
            raise AuthenticationException(detail="User not found")

        if not user.is_active:
            logger.warning(
                f"Token validation failed - inactive user: {payload.get('sub')}"
            )
            raise AuthenticationException(detail="User account is not active")

        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "token_expires": payload.get("exp"),
        }

    async def refresh_tokens(self, db, refresh_token: str) -> Dict[str, str]:
        payload = self.token_service.verify_token(refresh_token, token_type="refresh")
        user = await self.user_service.get_user_by_email(db, payload.get("sub"))

        if not user:
            logger.warning(
                f"Token refresh failed - user not found: {payload.get('sub')}"
            )
            raise AuthenticationException(detail="User not found")

        if not user.is_active:
            logger.warning(
                f"Token refresh failed - inactive user: {payload.get('sub')}"
            )
            raise AuthenticationException(detail="User account is not active")

        access_token = self.token_service.create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        new_refresh_token = self.token_service.create_refresh_token(
            data={"sub": user.email}, expires_delta=timedelta(days=7)
        )

        logger.info(f"Tokens refreshed successfully for user: {user.email}")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
