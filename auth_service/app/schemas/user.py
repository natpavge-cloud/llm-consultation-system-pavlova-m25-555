from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPublic(BaseModel):
    """Публичное представление пользователя (без чувствительных данных)"""
    
    id: int = Field(..., description="ID пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    role: str = Field(..., description="Роль пользователя")
    created_at: datetime = Field(..., description="Дата создания аккаунта")
    
    # Используем современный ConfigDict для Pydantic V2
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "email": "user@example.com",
                    "role": "user",
                    "created_at": "2024-01-15T10:30:00"
                }
            ]
        }    )
UserResponse = UserPublic
RegisterRequest = UserPublic
UserCreate = UserPublic
