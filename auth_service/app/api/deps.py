from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения сессии базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_users_repo(
    session: AsyncSession = Depends(get_db)
) -> UsersRepository:
    """
    Фабрика для создания репозитория пользователей
    """
    return UsersRepository(session)


def get_auth_uc(
    users_repo: UsersRepository = Depends(get_users_repo)
) -> AuthUseCase:
    """
    Фабрика для создания UseCase аутентификации
    """
    return AuthUseCase(users_repo)


async def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None
) -> int:
    """
    Получить ID текущего пользователя из JWT токена
    """
    if not authorization:
        raise InvalidTokenError("Authorization header is missing")
    
    # Проверка формата: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise InvalidTokenError("Invalid authorization header format")
    
    token = parts[1]
    
    try:
        # Декодирование токена
        payload = decode_token(token)
        
        # Извлечение user_id из поля 'sub'
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidTokenError("Token payload is invalid")
        
        return int(user_id_str)
        
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError("Token is invalid")
    except ValueError:
        raise InvalidTokenError("Invalid user ID in token")


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    users_repo: UsersRepository = Depends(get_users_repo)
):
    """
    Получить текущего пользователя из базы данных
    """
    from app.core.exceptions import UserNotFoundError
    
    user = await users_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundError("User from token not found")
    
    return user
