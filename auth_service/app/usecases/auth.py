from datetime import timedelta

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError, UserNotFoundError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UsersRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import RegisterRequest as UserCreate
from app.schemas.user import UserPublic


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo
    
    async def register_user(self, user_in: UserCreate) -> UserPublic: 
        # данные из объекта user_in, который пришел из роутера
        existing_user = await self.users_repo.get_by_email(user_in.email)
        if existing_user:
            raise UserAlreadyExistsError()
        
        # Хеширование пароля из объекта
        password_hash = hash_password(user_in.password)
        
        # Создание пользователя
        user = await self.users_repo.create(
            email=user_in.email,
            password_hash=password_hash,
            role="user"
        )
        
        return UserPublic.model_validate(user)
    
    async def login_user(self, email: str, password: str) -> TokenResponse: # Изменили имя
        user = await self.users_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
    
    async def me(self, user_id: int) -> UserPublic:
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        
        return UserPublic.model_validate(user)
    