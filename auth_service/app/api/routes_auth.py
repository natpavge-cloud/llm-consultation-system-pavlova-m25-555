from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.db.session import get_db
from app.repositories.users import UsersRepository as UserRepository
from app.schemas.auth import RegisterRequest as UserCreate
from app.schemas.auth import TokenResponse as Token
from app.schemas.user import UserPublic as UserResponse
from app.usecases.auth import AuthUseCase

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_usecase = AuthUseCase(user_repo)
    return await auth_usecase.register_user(user_in)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_usecase = AuthUseCase(user_repo)
    return await auth_usecase.login_user(form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return current_user
