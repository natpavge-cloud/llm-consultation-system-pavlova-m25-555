from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Базовый класс для HTTP исключений"""
    
    def __init__(self, detail: str = None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.default_detail
        )


class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь с таким email уже существует"""
    status_code = status.HTTP_409_CONFLICT
    default_detail = "User with this email already exists"


class InvalidCredentialsError(BaseHTTPException):
    """Неверные учетные данные"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid email or password"


class InvalidTokenError(BaseHTTPException):
    """Невалидный токен"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid authentication token"
    
    def __init__(self, detail: str = None):
        super().__init__(detail)
        self.headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredError(BaseHTTPException):
    """Токен истёк"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication token has expired"
    
    def __init__(self, detail: str = None):
        super().__init__(detail)
        self.headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "User not found"


class PermissionDeniedError(BaseHTTPException):
    """Недостаточно прав доступа"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Permission denied"
    