"""
Pydantic models for Authentication module.
Handles data validation for user registration, login, and responses.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """Base model with shared user attributes."""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=50, 
        description="Unique username (3-50 characters)"
    )
    full_name: Optional[str] = Field(
        None, 
        max_length=100, 
        description="User's full name"
    )


class UserCreate(UserBase):
    """Model for user registration (requires password)."""
    password: str = Field(
        ..., 
        min_length=6, 
        description="Password must be at least 6 characters"
    )


class UserUpdate(BaseModel):
    """Model for updating user data (PUT method)."""
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6)


class UserLogin(BaseModel):
    """Model for user login credentials."""
    username: str
    password: str


class UserResponse(UserBase):
    """Model for returning user data (NEVER includes password)."""
    id: str
    created_at: datetime
    
    # Pydantic v2 config to allow reading from ORM/Dict objects
    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Model for authentication token response."""
    access_token: str
    token_type: str = "bearer"