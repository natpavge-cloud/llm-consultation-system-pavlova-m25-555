from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Схема запроса регистрации пользователя"""
    
    email: EmailStr = Field(
        ...,
        description="Email пользователя",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль (минимум 8 символов)",
        examples=["SecurePassword123"]
    )


class TokenResponse(BaseModel):
    """Схема ответа с токеном"""
    
    access_token: str = Field(
        ...,
        description="JWT токен доступа"
    )
    token_type: str = Field(
        default="bearer",
        description="Тип токена"
    )


class LoginResponse(TokenResponse):
    """Схема ответа при успешном входе (расширение TokenResponse)"""
    pass

# псевдонимы, чтобы импорты в роутере не падали
Token = TokenResponse
UserCreate = RegisterRequest
