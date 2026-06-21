"""
Tests for the Product/Files module.
Covers CRUD operations (Create, Read, Update, Delete) for workspace files.
Uses unique names to avoid conflicts with existing database records.
"""

import pytest
import uuid


def unique_filename() -> str:
    """Generate a unique file name for testing."""
    return f"file_{uuid.uuid4().hex[:8]}.pdf"


@pytest.mark.asyncio
async def test_create_product(client):
    """Test POST /api/products/ - successful creation."""
    payload = {
        "name": unique_filename(),
        "category": "document",
        "file_path": "/workspace/test/report.pdf",
        "file_size": 2048,
        "mime_type": "application/pdf",
        "description": "Test file",
        "tags": ["test", "pdf"],
        "is_archived": False
    }
    response = await client.post("/api/products/", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["category"] == "document"
    assert data["file_size"] == 2048
    assert data["mime_type"] == "application/pdf"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_all_products(client):
    """Test GET /api/products/ - retrieve all files."""
    # Create a file first to ensure the list is not empty
    payload = {
        "name": unique_filename(),
        "category": "image",
        "file_path": "/workspace/test/image.png",
        "file_size": 5120,
        "mime_type": "image/png"
    }
    await client.post("/api/products/", json=payload)
    
    # Get all products
    response = await client.get("/api/products/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_product_by_id(client):
    """Test GET /api/products/{id} - retrieve specific file."""
    # Create product
    create_payload = {
        "name": unique_filename(),
        "category": "spreadsheet",
        "file_path": "/workspace/test/data.xlsx",
        "file_size": 10240,
        "mime_type": "application/vnd.ms-excel"
    }
    create_response = await client.post("/api/products/", json=create_payload)
    product_id = create_response.json()["id"]
    
    # Get product by ID
    response = await client.get(f"/api/products/{product_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == create_payload["name"]


@pytest.mark.asyncio
async def test_get_product_invalid_id(client):
    """Test GET /api/products/{id} - invalid ID should return 404."""
    response = await client.get("/api/products/invalid_id_format")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_product(client):
    """Test PUT /api/products/{id} - update file metadata."""
    # Create product
    create_payload = {
        "name": unique_filename(),
        "category": "document",
        "file_path": "/workspace/test/doc.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf"
    }
    create_response = await client.post("/api/products/", json=create_payload)
    product_id = create_response.json()["id"]
    
    # Update product
    update_payload = {
        "name": "updated_file.pdf",
        "is_archived": True
    }
    response = await client.put(f"/api/products/{product_id}", json=update_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "updated_file.pdf"
    assert data["is_archived"] is True


@pytest.mark.asyncio
async def test_delete_product(client):
    """Test DELETE /api/products/{id} - delete file record."""
    # Create product
    create_payload = {
        "name": unique_filename(),
        "category": "archive",
        "file_path": "/workspace/test/old.zip",
        "file_size": 4096,
        "mime_type": "application/zip"
    }
    create_response = await client.post("/api/products/", json=create_payload)
    product_id = create_response.json()["id"]
    
    # Delete product
    delete_response = await client.delete(f"/api/products/{product_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    get_response = await client.get(f"/api/products/{product_id}")
    assert get_response.status_code == 404