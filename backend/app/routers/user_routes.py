"""
User REST Routes.
Exposes the UserController via HTTP endpoints (GET, POST, PUT, DELETE).
"""

from fastapi import APIRouter, HTTPException, status

from app.database.mongodb import MongoDB
from app.controllers.user_controller import UserController
from app.models.user import UserCreate, UserUpdate, UserResponse

# Initialize router with prefix and tag for Swagger UI
router = APIRouter(prefix="/api/users", tags=["Users Management"])


def get_user_controller() -> UserController:
    """Dependency to get an instance of UserController with the DB connection."""
    return UserController(MongoDB.get_database())


@router.post(
    "/", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new workspace user. Requires unique username and email."
)
async def create_user(user_data: UserCreate):
    """POST: Create a new user."""
    controller = get_user_controller()
    try:
        return await controller.create(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/", 
    response_model=list[UserResponse],
    summary="Get all users",
    description="Retrieves a list of all registered workspace users."
)
async def get_all_users():
    """GET: Retrieve all users."""
    controller = get_user_controller()
    return await controller.get_all()


@router.get(
    "/{user_id}", 
    response_model=UserResponse,
    summary="Get user by ID",
    description="Retrieves a specific user by their MongoDB ID."
)
async def get_user_by_id(user_id: str):
    """GET: Retrieve a single user by ID."""
    controller = get_user_controller()
    user = await controller.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Updates the data of an existing user. Only provided fields are updated."
)
async def update_user(user_id: str, user_data: UserUpdate):
    """PUT: Update an existing user."""
    controller = get_user_controller()
    updated_user = await controller.update(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return updated_user


@router.delete(
    "/{user_id}",
    summary="Delete user",
    description="Permanently deletes a user from the workspace."
)
async def delete_user(user_id: str):
    """DELETE: Delete a user by ID."""
    controller = get_user_controller()
    success = await controller.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return {"message": "User successfully deleted"}