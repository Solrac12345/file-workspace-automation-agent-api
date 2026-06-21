"""
Pydantic models for Service/Automation Rules module.
Defines the structure for workspace automation rules.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FileAction(str, Enum):
    """Enumeration of available automation actions."""
    MOVE = "move"
    RENAME = "rename"
    CLASSIFY = "classify"
    DELETE = "delete"


class FileType(str, Enum):
    """Enumeration of target file types for the rules."""
    PDF = "pdf"
    IMAGE = "image"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    ALL = "all"


class ServiceBase(BaseModel):
    """Base model with shared automation rule attributes."""
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=100, 
        description="Name of the automation rule"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Detailed description of what the rule does"
    )
    file_type: FileType = Field(
        ..., 
        description="Target file type for this rule"
    )
    action: FileAction = Field(
        ..., 
        description="Action to perform on the file"
    )
    destination: str = Field(
        ..., 
        description="Destination folder or pattern for the action"
    )
    is_active: bool = Field(
        default=True, 
        description="Whether the rule is currently active"
    )


class ServiceCreate(ServiceBase):
    """Model for creating a new automation rule."""
    pass  # Inherits all fields from ServiceBase


class ServiceUpdate(BaseModel):
    """Model for updating an existing automation rule (all fields optional)."""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    file_type: Optional[FileType] = None
    action: Optional[FileAction] = None
    destination: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    """Model for returning rule data."""
    id: str = Field(..., description="MongoDB document ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Pydantic v2 config to allow reading from ORM/Dict objects
    model_config = {"from_attributes": True}