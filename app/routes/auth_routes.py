from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.auth_controller import AuthController
from app.models.user import UserCreate, UserRead
from app.utils.auth import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """Register a new user"""
    user = await AuthController.register(session, user_data)
    return user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """Login and get access token"""
    user = await AuthController.authenticate_user(session, form_data.username, form_data.password)
    return AuthController.create_token(user)


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user
