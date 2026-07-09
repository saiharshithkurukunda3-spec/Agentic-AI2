from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserRegister(UserBase):
    password: str = Field(..., min_length=6, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: str = Field(..., alias="_id")
    created_at: datetime

    # In Pydantic v2, we use ConfigDict
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "_id": "60c72b2f9b1d8b2a1c8b4567",
                "created_at": "2026-07-09T12:00:00Z"
            }
        }
    )

class UserDB(UserBase):
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True
    )
