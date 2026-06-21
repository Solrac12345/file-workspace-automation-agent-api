"""
Tests for the Automation Services/Rules module.
Covers CRUD operations (Create, Read, Update, Delete) for workspace rules.
Uses unique names to avoid conflicts with existing database records.
"""

import pytest
import uuid


def unique_rule_name() -> str:
    """Generate a unique rule name for testing."""
    return f"Rule_{uuid.uuid4().hex[:8]}"


@pytest.mark.asyncio
async def test_create_service(client):
    """Test POST /api/services/ - successful creation."""
    payload = {
        "name": unique_rule_name(),
        "description": "Automatically move PDF files",
        "file_type": "pdf",
        "action": "move",
        "destination": "/workspace/pdfs/",
        "is_active": True
    }
    response = await client.post("/api/services/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["file_type"] == "pdf"
    assert data["action"] == "move"
    assert data["destination"] == "/workspace/pdfs/"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_all_services(client):
    """Test GET /api/services/ - retrieve all rules."""
    # Create a rule first to ensure the list is not empty
    payload = {
        "name": unique_rule_name(),
        "file_type": "image",
        "action": "classify",
        "destination": "/workspace/images/"
    }
    await client.post("/api/services/", json=payload)
    
    # Get all services
    response = await client.get("/api/services/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_service_by_id(client):
    """Test GET /api/services/{id} - retrieve specific rule."""
    # Create service
    create_payload = {
        "name": unique_rule_name(),
        "file_type": "document",
        "action": "rename",
        "destination": "/workspace/docs/"
    }
    create_response = await client.post("/api/services/", json=create_payload)
    service_id = create_response.json()["id"]
    
    # Get service by ID
    response = await client.get(f"/api/services/{service_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == service_id
    assert data["name"] == create_payload["name"]


@pytest.mark.asyncio
async def test_get_service_invalid_id(client):
    """Test GET /api/services/{id} - invalid ID should return 404."""
    response = await client.get("/api/services/invalid_id_format")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_service(client):
    """Test PUT /api/services/{id} - update rule configuration."""
    # Create service
    create_payload = {
        "name": unique_rule_name(),
        "file_type": "spreadsheet",
        "action": "move",
        "destination": "/workspace/excel/"
    }
    create_response = await client.post("/api/services/", json=create_payload)
    service_id = create_response.json()["id"]
    
    # Update service
    update_payload = {
        "name": "Updated Rule Name",
        "is_active": False
    }
    response = await client.put(f"/api/services/{service_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Rule Name"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_delete_service(client):
    """Test DELETE /api/services/{id} - delete rule."""
    # Create service
    create_payload = {
        "name": unique_rule_name(),
        "file_type": "all",
        "action": "delete",
        "destination": "/trash/"
    }
    create_response = await client.post("/api/services/", json=create_payload)
    service_id = create_response.json()["id"]
    
    # Delete service
    delete_response = await client.delete(f"/api/services/{service_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    get_response = await client.get(f"/api/services/{service_id}")
    assert get_response.status_code == 404