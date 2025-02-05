import bcrypt  
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.exceptions import DuplicateEntityException, RegistrationException, AuthenticationException

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
            # Hash the password directly using bcrypt (ensure it's in bytes)
            hashed_password = bcrypt.hashpw(user_create.password.encode('utf-8'), bcrypt.gensalt())
            
            # Create new user instance
            db_user = User(
                email=user_create.email,
                full_name=user_create.full_name,
                hashed_password=hashed_password,  # Storing as bytes
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
        
    @staticmethod
    async def authenticate_user(
        db: AsyncSession, 
        login_data: UserLogin
    ) -> User:
        """
        Authenticate a user and return the user object if credentials are valid.
        
        Args:
            db (AsyncSession): The database session
            login_data (UserLogin): User login credentials
        
        Returns:
            User: The authenticated user
        
        Raises:
            AuthenticationException: If authentication fails
        """
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        # Check if user exists and password is correct
        if not user:
            raise AuthenticationException(
                detail="Incorrect email or password"
            )

        # Ensure hashed_password is in bytes before comparing
        stored_hashed_password = user.hashed_password.encode('utf-8') if isinstance(user.hashed_password, str) else user.hashed_password

        # Check if the password matches using bcrypt
        if not bcrypt.checkpw(login_data.password.encode('utf-8'), stored_hashed_password):
            raise AuthenticationException(
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationException(
                detail="User account is not active"
            )
        
        return user
    
    @staticmethod
    def create_access_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create an access token with optional custom expiration."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def create_refresh_token(
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token with optional custom expiration."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
    
    @staticmethod
    def verify_token(token: str, token_type: str = None) -> Dict:
        """
        Verify and decode a JWT token with optional type checking.
        
        Args:
            token (str): The JWT token to verify
            token_type (str, optional): Expected token type ('access' or 'refresh')
        
        Returns:
            dict: The decoded token payload
        """
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            
            # Optional type checking
            if token_type and payload.get("type") != token_type:
                raise AuthenticationException(detail=f"Invalid {token_type} token")
            
            return payload
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationException(detail="Token has expired")
        except JWTError:
            raise AuthenticationException(detail="Invalid token")
        
    @staticmethod
    async def validate_access_token(
        db: AsyncSession, 
        access_token: str
    ) -> Dict[str, Any]:
        """
        Validate access token and retrieve user details.
        
        Args:
            db (AsyncSession): Database session
            access_token (str): JWT access token
        
        Returns:
            dict: User validation details
        
        Raises:
            AuthenticationException: If token is invalid or user not found
        """
        # Verify the token
        payload = AuthHandler.verify_token(access_token, token_type="access")
        
        # Retrieve user based on email from token payload
        result = await db.execute(
            select(User).where(User.email == payload.get("sub"))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise AuthenticationException(detail="User not found")
        
        if not user.is_active:
            raise AuthenticationException(detail="User account is not active")
        
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "token_expires": payload.get("exp")
        }
    
    @staticmethod
    async def refresh_tokens(
        db: AsyncSession, 
        refresh_token: str
    ) -> Dict[str, str]:
        """
        Refresh access and refresh tokens.
        
        Args:
            db (AsyncSession): Database session
            refresh_token (str): Current refresh token
        
        Returns:
            dict: New access and refresh tokens
        """
        # Verify refresh token
        payload = AuthHandler.verify_token(refresh_token, token_type="refresh")
        
        # Retrieve user based on email from refresh token payload
        result = await db.execute(
            select(User).where(User.email == payload.get("sub"))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise RefreshTokenException(detail="User not found")
        
        if not user.is_active:
            raise RefreshTokenException(detail="User account is not active")
        
        # Generate new tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=7)
        
        new_access_token = AuthHandler.create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
        
        new_refresh_token = AuthHandler.create_refresh_token(
            data={"sub": user.email},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }