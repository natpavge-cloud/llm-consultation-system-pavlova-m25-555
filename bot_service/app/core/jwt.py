from typing import Dict
from jose import JWTError, jwt, ExpiredSignatureError

from app.core.config import settings


class TokenValidationError(Exception):
    """Ошибка валидации токена"""
    pass


class TokenExpiredError(TokenValidationError):
    """Токен истёк"""
    pass


def decode_and_validate(token: str) -> Dict:
    """
    Декодирует и валидирует JWT токен
    """
    try:
        # Декодирование токена
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG]
        )
        
        # Проверка наличия обязательных полей
        if "sub" not in payload:
            raise TokenValidationError("Token payload is missing 'sub' field")
        
        if "exp" not in payload:
            raise TokenValidationError("Token payload is missing 'exp' field")
        
        return payload
        
    except ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except JWTError as e:
        raise TokenValidationError(f"Invalid token: {str(e)}")
    