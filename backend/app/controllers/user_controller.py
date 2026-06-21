"""
User Controller.
Handles business logic for user management (CRUD).
Implements Object-Oriented Programming (OOP) principles.
"""

from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext

from app.models.user import UserCreate, UserUpdate, UserResponse


class UserController:
    """
    Controller class for User module.
    Encapsulates database operations, password hashing, and data transformation.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize controller with database connection and security context."""
        self.db = db
        self.collection = db.users
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def _hash_password(self, password: str) -> str:
        """Private method to hash passwords (Encapsulation)."""
        return self.pwd_context.hash(password)

    def _parse_user(self, doc: dict) -> Optional[UserResponse]:
        """Private method to transform MongoDB document to Pydantic model."""
        if not doc:
            return None
        
        # Use .get() with defaults to handle missing fields gracefully
        return UserResponse(
            id=str(doc["_id"]),
            username=doc.get("username", "unknown"),
            email=doc.get("email", f"{doc.get('username', 'unknown')}@noemail.com"),
            full_name=doc.get("full_name", doc.get("username", "Unknown User")),
            role=doc.get("role", "viewer"),
            created_at=doc.get("created_at", datetime.now(timezone.utc)),
            updated_at=doc.get("updated_at"),
        )

    async def create(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user.
        Checks for existing username/email and hashes the password.
        """
        # Check if username or email already exists
        existing = await self.collection.find_one({
            "$or": [
                {"username": user_data.username},
                {"email": user_data.email}
            ]
        })
        if existing:
            raise ValueError("Username or email already exists")

        now = datetime.now(timezone.utc)
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": user_data.role.value if hasattr(user_data.role, 'value') else user_data.role,
            "password": self._hash_password(user_data.password),
            "created_at": now,
            "updated_at": now,
        }

        result = await self.collection.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        return self._parse_user(user_doc)

    async def get_all(self) -> list[UserResponse]:
        """Retrieve all users from the database."""
        cursor = self.collection.find({})
        users = []
        async for doc in cursor:
            user = self._parse_user(doc)
            if user:  # Solo agregar si no es None
                users.append(user)
        return users

    async def get_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Retrieve a single user by their MongoDB ID."""
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        
        doc = await self.collection.find_one({"_id": oid})
        return self._parse_user(doc)

    async def update(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """
        Update an existing user.
        Only updates fields that are provided (partial update).
        """
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None

        # Extract only the fields that were actually sent
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["password"] = self._hash_password(update_data["password"])
        
        # Handle Enum conversion for role
        if "role" in update_data and hasattr(update_data["role"], 'value'):
            update_data["role"] = update_data["role"].value

        update_data["updated_at"] = datetime.now(timezone.utc)

        result = await self.collection.find_one_and_update(
            {"_id": oid},
            {"$set": update_data},
            return_document=True
        )
        return self._parse_user(result)

    async def delete(self, user_id: str) -> bool:
        """Delete a user by their MongoDB ID."""
        try:
            oid = ObjectId(user_id)
        except Exception:
            return False
        
        result = await self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0