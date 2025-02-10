from typing import Optional

import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.core.exceptions import DuplicateEntityException, RegistrationException
from app.core.logger import logger
from app.interfaces.auth import IUserService
from app.models.user import User
from app.schemas.user import UserCreate


class UserService(IUserService):
    async def register_user(self, db, user_create: UserCreate) -> User:
        # Check if user already exists
        existing_user = await self.get_user_by_email(db, user_create.email)
        if existing_user:
            raise DuplicateEntityException(
                detail="A user with this email is already registered"
            )

        try:
            hashed_password = bcrypt.hashpw(
                user_create.password.encode("utf-8"), bcrypt.gensalt()
            )

            db_user = User(
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password=hashed_password,
                is_active=user_create.is_active,
                is_superuser=user_create.is_superuser,
            )

            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)

            logger.info(f"User registered successfully: {user_create.email}")
            return db_user

        except IntegrityError:
            await db.rollback()
            logger.error(
                f"Registration failed - database constraint: {user_create.email}"
            )
            raise RegistrationException(
                detail="Unable to complete user registration due to a database constraint"
            )
        except Exception as e:
            await db.rollback()
            logger.error(f"Registration failed - unexpected error: {str(e)}")
            raise RegistrationException(
                detail=f"Unexpected error during user registration: {str(e)}"
            )

    async def get_user_by_email(self, db, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def verify_password(
        self, plain_password: str, hashed_password: bytes
    ) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            (
                hashed_password
                if isinstance(hashed_password, bytes)
                else hashed_password.encode("utf-8")
            ),
        )
