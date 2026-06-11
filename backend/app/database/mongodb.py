"""
MongoDB connection module using Motor (async driver).
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings


class MongoDB:
    """MongoDB connection manager using async Motor client."""

    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None

    @classmethod
    async def connect(cls) -> None:
        """Establish async connection to MongoDB Atlas."""
        cls.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )
        cls.db = cls.client[settings.DB_NAME]
        print(f"✅ Connected to MongoDB: {settings.DB_NAME}")

    @classmethod
    async def disconnect(cls) -> None:
        """Close MongoDB connection gracefully."""
        if cls.client is not None:
            cls.client.close()
            print("🔌 MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Return the database instance."""
        if cls.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return cls.db


async def ping_database() -> dict:
    """Test MongoDB connection by pinging the server."""
    try:
        db = MongoDB.get_database()
        await db.command("ping")
        return {
            "status": "ok",
            "database": settings.DB_NAME,
            "message": "MongoDB connection successful",
        }
    except Exception as e:
        return {
            "status": "error",
            "database": settings.DB_NAME,
            "message": f"MongoDB connection failed: {str(e)}",
        }