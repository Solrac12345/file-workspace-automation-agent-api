"""
Tests for the Authentication module.
Covers registration, login, profile retrieval, and logout.
"""

import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    """Test POST /api/auth/register - successful registration."""
    payload = {
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    response = await client.post("/api/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "created_at" in data
    assert "password" not in data  # Security: password must not be returned


@pytest.mark.asyncio
async def test_register_duplicate_user(client):
    """Test POST /api/auth/register - duplicate username should fail."""
    payload = {
        "username": "duplicate",
        "password": "testpass123"
    }
    # First registration should succeed
    response1 = await client.post("/api/auth/register", json=payload)
    assert response1.status_code == 201
    
    # Second registration should fail
    response2 = await client.post("/api/auth/register", json=payload)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client):
    """Test POST /api/auth/login - successful authentication."""
    # Register user first
    register_payload = {
        "username": "loginuser",
        "password": "testpass123"
    }
    await client.post("/api/auth/register", json=register_payload)
    
    # Login
    login_payload = {
        "username": "loginuser",
        "password": "testpass123"
    }
    response = await client.post("/api/auth/login", json=login_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "loginuser"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    """Test POST /api/auth/login - invalid credentials should fail."""
    payload = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    response = await client.post("/api/auth/login", json=payload)
    
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client):
    """Test GET /api/auth/me - retrieve authenticated user profile."""
    # Register and login
    register_payload = {
        "username": "profileuser",
        "password": "testpass123",
        "full_name": "Profile User"
    }
    await client.post("/api/auth/register", json=register_payload)
    
    login_response = await client.post(
        "/api/auth/login",
        json={"username": "profileuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Get profile
    response = await client.get(
        "/api/auth/me",
        headers={"X-Token": token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "profileuser"
    assert data["full_name"] == "Profile User"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client):
    """Test GET /api/auth/me - invalid token should fail."""
    response = await client.get(
        "/api/auth/me",
        headers={"X-Token": "invalid-token"}
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client):
    """Test DELETE /api/auth/logout - invalidate token."""
    # Register and login
    register_payload = {
        "username": "logoutuser",
        "password": "testpass123"
    }
    await client.post("/api/auth/register", json=register_payload)
    
    login_response = await client.post(
        "/api/auth/login",
        json={"username": "logoutuser", "password": "testpass123"}
    )
    token = login_response.json()["access_token"]
    
    # Logout
    logout_response = await client.delete(
        "/api/auth/logout",
        headers={"X-Token": token}
    )
    assert logout_response.status_code == 200
    
    # Try to use token after logout - should fail
    profile_response = await client.get(
        "/api/auth/me",
        headers={"X-Token": token}
    )
    assert profile_response.status_code == 401