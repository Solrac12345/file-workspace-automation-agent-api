"""
Pydantic models for Product/Files module.
Defines the structure for workspace files managed by the automation agent.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    """Enumeration of file categories in the workspace."""
    DOCUMENT = "document"
    IMAGE = "image"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    ARCHIVE = "archive"
    OTHER = "other"


class ProductBase(BaseModel):
    """Base model with shared file attributes."""
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255, 
        description="File name"
    )
    category: ProductCategory = Field(
        ..., 
        description="Category of the file"
    )
    file_path: str = Field(
        ..., 
        description="Path to the file in the workspace"
    )
    file_size: int = Field(
        ..., 
        ge=0, 
        description="File size in bytes"
    )
    mime_type: str = Field(
        ..., 
        description="MIME type of the file (e.g., application/pdf)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Optional description of the file"
    )
    tags: list[str] = Field(
        default_factory=list, 
        description="List of tags for classification"
    )
    is_archived: bool = Field(
        default=False, 
        description="Whether the file is archived"
    )


class ProductCreate(ProductBase):
    """Model for creating a new file record."""
    owner_id: Optional[str] = Field(
        None, 
        description="ID of the user who owns the file"
    )


class ProductUpdate(BaseModel):
    """Model for updating an existing file record (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[ProductCategory] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    tags: Optional[list[str]] = None
    is_archived: Optional[bool] = None


class ProductResponse(ProductBase):
    """Model for returning file data."""
    id: str = Field(..., description="MongoDB document ID")
    owner_id: Optional[str] = Field(None, description="ID of the file owner")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Pydantic v2 config to allow reading from ORM/Dict objects
    model_config = {"from_attributes": True}