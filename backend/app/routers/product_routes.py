"""
Product/Files REST Routes.
Exposes the ProductController via HTTP endpoints (GET, POST, PUT, DELETE).
"""

from fastapi import APIRouter, HTTPException, status

from app.database.mongodb import MongoDB
from app.controllers.product_controller import ProductController
from app.models.product import ProductCreate, ProductUpdate, ProductResponse

# Initialize router with prefix and tag for Swagger UI
router = APIRouter(prefix="/api/products", tags=["Workspace Products"])


def get_product_controller() -> ProductController:
    """Dependency to get an instance of ProductController with the DB connection."""
    return ProductController(MongoDB.get_database())


@router.post(
    "/", 
    response_model=ProductResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new file",
    description="Registers a new file record in the workspace (e.g., a PDF or image)."
)
async def create_product(product_data: ProductCreate):
    """POST: Register a new file."""
    controller = get_product_controller()
    return await controller.create(product_data)


@router.get(
    "/", 
    response_model=list[ProductResponse],
    summary="Get all files",
    description="Retrieves a list of all registered files in the workspace."
)
async def get_all_products():
    """GET: Retrieve all files."""
    controller = get_product_controller()
    return await controller.get_all()


@router.get(
    "/{product_id}", 
    response_model=ProductResponse,
    summary="Get file by ID",
    description="Retrieves a specific file record by its MongoDB ID."
)
async def get_product_by_id(product_id: str):
    """GET: Retrieve a single file by ID."""
    controller = get_product_controller()
    product = await controller.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File record not found"
        )
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update file record",
    description="Updates the metadata of an existing file record."
)
async def update_product(product_id: str, product_data: ProductUpdate):
    """PUT: Update an existing file record."""
    controller = get_product_controller()
    updated_product = await controller.update(product_id, product_data)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File record not found"
        )
    return updated_product


@router.delete(
    "/{product_id}",
    summary="Delete file record",
    description="Permanently deletes a file record from the workspace database."
)
async def delete_product(product_id: str):
    """DELETE: Delete a file record by ID."""
    controller = get_product_controller()
    success = await controller.delete(product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="File record not found"
        )
    return {"message": "File record successfully deleted"}