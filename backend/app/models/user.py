"""
Pydantic models for User module.
Handles data validation for user management (CRUD operations).
Adapted for File & Workspace Automation Agent workspace users.
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """Enumeration of available user roles in the workspace."""
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base model with shared user attributes."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name"
    )
    role: UserRole = Field(
        default=UserRole.VIEWER,
        description="User role in the workspace"
    )


class UserCreate(UserBase):
    """Model for creating a new user (requires password)."""
    password: str = Field(
        ...,
        min_length=6,
        description="Password must be at least 6 characters"
    )


class UserUpdate(BaseModel):
    """Model for updating user data (all fields optional for PUT method)."""
    email: Optional[EmailStr] = Field(None, description="New email address")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = Field(None, description="New role")
    password: Optional[str] = Field(None, min_length=6, description="New password")


class UserResponse(UserBase):
    """Model for returning user data (NEVER includes password)."""
    id: str = Field(..., description="MongoDB document ID")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Pydantic v2 config to allow reading from ORM/Dict objects
    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    """Model for returning a list of users with pagination info."""
    users: list[UserResponse]
    total: int = Field(..., description="Total number of users")
    page: int = Field(default=1, description="Current page number")
    per_page: int = Field(default=10, description="Users per page")