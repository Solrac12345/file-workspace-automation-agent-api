"""
Authentication REST Routes.
Exposes the AuthController via HTTP endpoints (GET, POST, PUT, DELETE).
"""

from fastapi import APIRouter, HTTPException, Header, status

from app.database.mongodb import MongoDB
from app.controllers.auth_controller import AuthController
from app.models.auth import UserCreate, UserLogin, UserUpdate, UserResponse, Token

# Initialize router with prefix and tag for Swagger UI
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def get_auth_controller() -> AuthController:
    """Dependency to get an instance of AuthController with the DB connection."""
    return AuthController(MongoDB.get_database())


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account in the database."
)
async def register_user(user_data: UserCreate):
    """POST: Register a new user."""
    controller = get_auth_controller()
    try:
        return await controller.register(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login", 
    response_model=Token,
    summary="User login",
    description="Authenticates user and returns a bearer token."
)
async def login_user(credentials: UserLogin):
    """POST: Authenticate user and get token."""
    controller = get_auth_controller()
    try:
        return await controller.login(credentials)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get(
    "/me", 
    response_model=UserResponse,
    summary="Get current user profile",
    description="Retrieves the profile of the authenticated user using a token."
)
async def get_current_user(x_token: str = Header(..., alias="X-Token")):
    """GET: Get current user data using the token in the header."""
    controller = get_auth_controller()
    user = await controller.get_current_user(x_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid or expired token"
        )
    return user


@router.put(
    "/password",
    summary="Update user password",
    description="Updates the password for the authenticated user."
)
async def update_password(
    x_token: str = Header(..., alias="X-Token"),
    update_data: UserUpdate = None # In a real app, we'd validate new_password is present
):
    """PUT: Update user password."""
    # For simplicity in this step, we'll just accept a new_password in the body or query.
    # Let's use a simple query parameter for the new password to keep it easy to test.
    pass # Replaced by the endpoint below for better testing


@router.put(
    "/update-password",
    summary="Update user password",
    description="Updates the password for the authenticated user."
)
async def update_password_endpoint(
    x_token: str = Header(..., alias="X-Token"),
    new_password: str = Header(..., alias="X-New-Password")
):
    """PUT: Update password using headers for easy Swagger testing."""
    controller = get_auth_controller()
    try:
        success = await controller.update_password(x_token, new_password)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"message": "Password updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.delete(
    "/logout",
    summary="User logout",
    description="Invalidates the current session token."
)
async def logout_user(x_token: str = Header(..., alias="X-Token")):
    """DELETE: Logout and invalidate token."""
    controller = get_auth_controller()
    success = await controller.logout(x_token)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token not found or already invalidated")
    return {"message": "Successfully logged out"}