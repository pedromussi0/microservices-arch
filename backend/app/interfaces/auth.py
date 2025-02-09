from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Dict, Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin


class IUserService(ABC):
    @abstractmethod
    async def register_user(self, db, user_create: UserCreate) -> User:
        pass

    @abstractmethod
    async def get_user_by_email(self, db, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def verify_password(
        self, plain_password: str, hashed_password: bytes
    ) -> bool:
        pass


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        pass

    @abstractmethod
    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        pass

    @abstractmethod
    def verify_token(self, token: str, token_type: str = None) -> Dict:
        pass


class IAuthService(ABC):
    @abstractmethod
    async def authenticate_user(self, db, login_data: UserLogin) -> User:
        pass

    @abstractmethod
    async def validate_access_token(self, db, access_token: str) -> Dict:
        pass

    @abstractmethod
    async def refresh_tokens(self, db, refresh_token: str) -> Dict[str, str]:
        pass
