"""
Authentication Controller.
Handles business logic for user registration, login, and token management.
Implements Object-Oriented Programming (OOP) principles.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext

from app.models.auth import UserCreate, UserLogin, UserResponse


class AuthController:
    """
    Controller class for Authentication module.
    Encapsulates password hashing, user creation, and in-memory token management.
    """
    active_tokens: dict[str, dict] = {}

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize controller with database connection and security context."""
        self.db = db
        self.collection = db.users
        # Context for hashing passwords securely using bcrypt
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        """Hash a plain text password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed one."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def register(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user in the database.
        Returns the created user (without password).
        """
        # Check if username already exists
        existing_user = await self.collection.find_one({"username": user_data.username})
        if existing_user:
            raise ValueError("Username already exists")

        # Create user document
        user_doc = {
            "username": user_data.username,
            "full_name": user_data.full_name or user_data.username,
            "password": self.hash_password(user_data.password),
            "created_at": datetime.now(timezone.utc),
        }

        # Insert into database
        result = await self.collection.insert_one(user_doc)
        user_doc["id"] = str(result.inserted_id)

        # Return user response (Pydantic model excludes password automatically)
        return UserResponse(
            id=str(result.inserted_id),
            username=user_doc["username"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"],
        )

    async def login(self, credentials: UserLogin) -> dict:
        """
        Authenticate user and generate a simple in-memory token.
        Returns a dictionary with the token and user info.
        """
        # Find user by username
        user = await self.collection.find_one({"username": credentials.username})
        if not user:
            raise ValueError("Invalid credentials")

        # Verify password
        if not self.verify_password(credentials.password, user["password"]):
            raise ValueError("Invalid credentials")

        # Generate simple token (UUID)
        token = str(uuid.uuid4())
        
        # Store token in memory
        self.active_tokens[token] = {
            "user_id": str(user["_id"]),
            "username": user["username"],
        }

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "full_name": user.get("full_name"),
            }
        }

    async def get_current_user(self, token: str) -> Optional[UserResponse]:
        """
        Retrieve user data based on a valid token.
        Used for the GET method in the auth module.
        """
        token_data = self.active_tokens.get(token)
        if not token_data:
            return None

        # Fetch user from DB to get latest data
        from bson import ObjectId
        user = await self.collection.find_one({"_id": ObjectId(token_data["user_id"])})
        
        if not user:
            return None

        return UserResponse(
            id=str(user["_id"]),
            username=user["username"],
            full_name=user.get("full_name"),
            created_at=user["created_at"],
        )

    async def update_password(self, token: str, new_password: str) -> bool:
        """
        Update user password.
        Used for the PUT method in the auth module.
        """
        token_data = self.active_tokens.get(token)
        if not token_data:
            raise ValueError("Invalid or expired token")

        from bson import ObjectId
        result = await self.collection.update_one(
            {"_id": ObjectId(token_data["user_id"])},
            {"$set": {"password": self.hash_password(new_password)}}
        )
        return result.modified_count > 0

    async def logout(self, token: str) -> bool:
        """
        Invalidate token (Logout).
        Used for the DELETE method in the auth module.
        """
        if token in self.active_tokens:
            del self.active_tokens[token]
            return True
        return False