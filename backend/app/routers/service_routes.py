"""
Service/Automation Rules REST Routes.
Exposes the ServiceController via HTTP endpoints (GET, POST, PUT, DELETE).
"""

from fastapi import APIRouter, HTTPException, status

from app.database.mongodb import MongoDB
from app.controllers.service_controller import ServiceController
from app.models.service import ServiceCreate, ServiceUpdate, ServiceResponse

# Initialize router with prefix and tag for Swagger UI
router = APIRouter(prefix="/api/services", tags=["Automation Services"])


def get_service_controller() -> ServiceController:
    """Dependency to get an instance of ServiceController with the DB connection."""
    return ServiceController(MongoDB.get_database())


@router.post(
    "/", 
    response_model=ServiceResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new automation rule",
    description="Creates a new rule for file automation (e.g., move PDFs to a specific folder)."
)
async def create_service(service_data: ServiceCreate):
    """POST: Create a new automation rule."""
    controller = get_service_controller()
    return await controller.create(service_data)


@router.get(
    "/", 
    response_model=list[ServiceResponse],
    summary="Get all automation rules",
    description="Retrieves a list of all configured workspace automation rules."
)
async def get_all_services():
    """GET: Retrieve all automation rules."""
    controller = get_service_controller()
    return await controller.get_all()


@router.get(
    "/{service_id}", 
    response_model=ServiceResponse,
    summary="Get rule by ID",
    description="Retrieves a specific automation rule by its MongoDB ID."
)
async def get_service_by_id(service_id: str):
    """GET: Retrieve a single automation rule by ID."""
    controller = get_service_controller()
    service = await controller.get_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Automation rule not found"
        )
    return service


@router.put(
    "/{service_id}",
    response_model=ServiceResponse,
    summary="Update automation rule",
    description="Updates the configuration of an existing automation rule."
)
async def update_service(service_id: str, service_data: ServiceUpdate):
    """PUT: Update an existing automation rule."""
    controller = get_service_controller()
    updated_service = await controller.update(service_id, service_data)
    if not updated_service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Automation rule not found"
        )
    return updated_service


@router.delete(
    "/{service_id}",
    summary="Delete automation rule",
    description="Permanently deletes an automation rule from the workspace."
)
async def delete_service(service_id: str):
    """DELETE: Delete an automation rule by ID."""
    controller = get_service_controller()
    success = await controller.delete(service_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Automation rule not found"
        )
    return {"message": "Automation rule successfully deleted"}