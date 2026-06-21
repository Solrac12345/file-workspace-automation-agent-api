"""
Tests for the User Management module.
Covers CRUD operations (Create, Read, Update, Delete) for workspace users.
Uses unique data to avoid conflicts with existing database records.
"""

import pytest
import uuid


def unique_username() -> str:
    """Generate a unique username for testing."""
    return f"user_{uuid.uuid4().hex[:8]}"


def unique_email() -> str:
    """Generate a unique email for testing."""
    return f"test_{uuid.uuid4().hex[:8]}@sena.edu.co"


@pytest.mark.asyncio
async def test_create_user(client):
    """Test POST /api/users/ - successful creation."""
    payload = {
        "username": unique_username(),
        "email": unique_email(),
        "full_name": "Test User Full Name",
        "password": "securepass123",
        "role": "operator"
    }
    response = await client.post("/api/users/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert data["role"] == "operator"
    assert "id" in data
    assert "password" not in data  # Security check


@pytest.mark.asyncio
async def test_create_duplicate_user(client):
    """Test POST /api/users/ - duplicate username/email should fail."""
    username = unique_username()
    email = unique_email()
    payload = {
        "username": username,
        "email": email,
        "full_name": "Duplicate User",
        "password": "securepass123",
        "role": "viewer"
    }
    
    # First creation should succeed
    response1 = await client.post("/api/users/", json=payload)
    assert response1.status_code == 201
    
    # Second creation should fail
    response2 = await client.post("/api/users/", json=payload)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_get_all_users(client):
    """Test GET /api/users/ - retrieve all users."""
    # Create a user first to ensure the list is not empty
    payload = {
        "username": unique_username(),
        "email": unique_email(),
        "full_name": "List User",
        "password": "securepass123",
        "role": "viewer"
    }
    await client.post("/api/users/", json=payload)
    
    # Get all users
    response = await client.get("/api/users/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_user_by_id(client):
    """Test GET /api/users/{id} - retrieve specific user."""
    # Create user
    create_payload = {
        "username": unique_username(),
        "email": unique_email(),
        "full_name": "Get By ID User",
        "password": "securepass123",
        "role": "admin"
    }
    create_response = await client.post("/api/users/", json=create_payload)
    user_id = create_response.json()["id"]
    
    # Get user by ID
    response = await client.get(f"/api/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["full_name"] == "Get By ID User"


@pytest.mark.asyncio
async def test_get_user_invalid_id(client):
    """Test GET /api/users/{id} - invalid ID should return 404."""
    response = await client.get("/api/users/invalid_id_format")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client):
    """Test PUT /api/users/{id} - update user data."""
    # Create user
    create_payload = {
        "username": unique_username(),
        "email": unique_email(),
        "full_name": "Original Name",
        "password": "securepass123",
        "role": "viewer"
    }
    create_response = await client.post("/api/users/", json=create_payload)
    user_id = create_response.json()["id"]
    
    # Update user
    update_payload = {
        "full_name": "Updated Name",
        "role": "admin"
    }
    response = await client.put(f"/api/users/{user_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_delete_user(client):
    """Test DELETE /api/users/{id} - delete user."""
    # Create user
    create_payload = {
        "username": unique_username(),
        "email": unique_email(),
        "full_name": "To Be Deleted",
        "password": "securepass123",
        "role": "viewer"
    }
    create_response = await client.post("/api/users/", json=create_payload)
    user_id = create_response.json()["id"]
    
    # Delete user
    delete_response = await client.delete(f"/api/users/{user_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    get_response = await client.get(f"/api/users/{user_id}")
    assert get_response.status_code == 404