from pydantic import BaseModel, EmailStr
from pydantic.types import StringConstraints
from typing import Optional
from datetime import datetime
from typing_extensions import Annotated  
from pydantic import ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: Annotated[str, StringConstraints(min_length=8)] 

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
