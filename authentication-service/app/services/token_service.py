from datetime import datetime, timedelta
from typing import Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.core.logger import logger
from app.interfaces.auth import ITokenService


class TokenService(ITokenService):
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire, "type": "access"})

        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
        )

    def create_refresh_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
        to_encode.update({"exp": expire, "type": "refresh"})

        return jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
        )

    def verify_token(self, token: str, token_type: str = None) -> Dict:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
            )

            if token_type and payload.get("type") != token_type:
                logger.warning(f"Invalid token type: expected {token_type}")
                raise AuthenticationException(detail=f"Invalid {token_type} token")

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise AuthenticationException(detail="Token has expired")
        except JWTError:
            logger.warning("Invalid token")
            raise AuthenticationException(detail="Invalid token")
