"""
Pytest configuration and shared fixtures.
Provides test client and database setup for all tests.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database.mongodb import MongoDB


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure anyio to use asyncio."""
    return "asyncio"


@pytest.fixture
async def client():
    """
    Async test client for making HTTP requests to the API.
    Automatically connects to MongoDB before tests and disconnects after.
    """
    # Connect to MongoDB before tests
    await MongoDB.connect()
    
    # Create async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Disconnect after tests
    await MongoDB.disconnect()