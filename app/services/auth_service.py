from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserCreate
from passlib.context import CryptContext
from app.core.exceptions import DuplicateEntityException, RegistrationException

class AuthHandler:
    @staticmethod
    async def register_user(
        db: AsyncSession, 
        user_create: UserCreate
    ) -> User:
        """
        Register a new user in the database.
        
        Args:
            db (AsyncSession): The database session
            user_create (UserCreate): User creation schema with registration details
        
        Returns:
            User: The newly created user
        
        Raises:
            DuplicateEntityException: If a user with the same email already exists
            RegistrationException: If there's an error during user registration
        """
        # Check if user already exists
        existing_user_query = await db.execute(
            select(User).where(User.email == user_create.email)
        )
        if existing_user_query.scalar_one_or_none():
            raise DuplicateEntityException(
                detail="A user with this email is already registered"
            )
        
        try:
            # Hash the password
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(user_create.password)
            
            # Create new user instance
            db_user = User(
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password=hashed_password,
                is_active=user_create.is_active,
                is_superuser=user_create.is_superuser
            )
            
            # Add and commit the new user
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            
            return db_user
        
        except IntegrityError:
            await db.rollback()
            raise RegistrationException(
                detail="Unable to complete user registration due to a database constraint"
            )
        except Exception as e:
            await db.rollback()
            raise RegistrationException(
                detail=f"Unexpected error during user registration: {str(e)}"
            )