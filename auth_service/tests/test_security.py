"""
Модульные тесты для функций безопасности Auth Service
"""
from datetime import datetime, timedelta

import pytest
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token, decode_token, hash_password, verify_password


class TestPasswordHashing:
    """Тесты хеширования паролей"""
    
    def test_hash_password_creates_hash(self):
        """Тест: хеш создаётся"""
        password = "SecurePassword123"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) > 0
        assert isinstance(hashed, str)
    
    def test_hash_not_equal_to_password(self):
        """Тест: хеш НЕ равен исходному паролю"""
        password = "MyPassword123"
        hashed = hash_password(password)
        
        # Важно: хеш не должен совпадать с паролем
        assert hashed != password
    
    def test_same_password_different_hashes(self):
        """Тест: один пароль даёт разные хеши (из-за соли)"""
        password = "TestPassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # bcrypt использует случайную соль
        assert hash1 != hash2
    
    def test_hash_contains_bcrypt_prefix(self):
        """Тест: хеш содержит префикс bcrypt"""
        password = "AnotherPassword"
        hashed = hash_password(password)
        
        # bcrypt хеши начинаются с $2b$
        assert hashed.startswith("$2b$")


class TestPasswordVerification:
    """Тесты проверки паролей"""
    
    def test_verify_correct_password(self):
        """Тест: правильный пароль проходит проверку"""
        password = "CorrectPassword123"
        hashed = hash_password(password)
        
        # Правильный пароль должен пройти verify
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Тест: неправильный пароль НЕ проходит проверку"""
        correct_password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        hashed = hash_password(correct_password)
        
        # Неправильный пароль не должен пройти verify
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_case_sensitive(self):
        """Тест: проверка чувствительна к регистру"""
        password = "Password123"
        hashed = hash_password(password)
        
        assert verify_password("password123", hashed) is False
        assert verify_password("PASSWORD123", hashed) is False
        assert verify_password("Password123", hashed) is True
    
    def test_verify_empty_password(self):
        """Тест: пустой пароль не проходит"""
        password = "RealPassword"
        hashed = hash_password(password)
        
        assert verify_password("", hashed) is False


class TestJWTCreation:
    """Тесты создания JWT токенов"""
    
    def test_create_access_token_returns_string(self):
        """Тест: токен возвращается как строка"""
        token = create_access_token(
            user_id=1,
            role="user"
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_can_be_decoded(self):
        """Тест: токен можно декодировать"""
        user_id = 42
        role = "admin"
        
        token = create_access_token(user_id=user_id, role=role)
        payload = decode_token(token)
        
        assert payload is not None
        assert isinstance(payload, dict)
    
    def test_token_contains_sub(self):
        """Тест: токен содержит поле sub (user_id)"""
        user_id = 123
        token = create_access_token(user_id=user_id, role="user")
        payload = decode_token(token)
        
        # sub должен присутствовать
        assert "sub" in payload
        assert payload["sub"] == str(user_id)
    
    def test_token_contains_role(self):
        """Тест: токен содержит поле role"""
        role = "moderator"
        token = create_access_token(user_id=1, role=role)
        payload = decode_token(token)
        
        # role должен присутствовать
        assert "role" in payload
        assert payload["role"] == role
    
    def test_token_contains_iat(self):
        """Тест: токен содержит поле iat (issued at)"""
        token = create_access_token(user_id=1, role="user")
        payload = decode_token(token)
        
        # iat должен присутствовать
        assert "iat" in payload
        assert isinstance(payload["iat"], (int, float))
    
    def test_token_contains_exp(self):
        """Тест: токен содержит поле exp (expiration)"""
        token = create_access_token(user_id=1, role="user")
        payload = decode_token(token)
        
        # exp должен присутствовать
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
    
    def test_sub_and_role_match_input(self):
        """Тест: sub и role совпадают с переданными значениями"""
        user_id = 999
        role = "superadmin"
        
        token = create_access_token(user_id=user_id, role=role)
        payload = decode_token(token)
        
        # Проверка точного совпадения
        assert payload["sub"] == str(user_id)
        assert payload["role"] == role
    
    def test_token_expiration_time(self):
        """Тест: время истечения токена корректно"""
        expires_delta = timedelta(minutes=30)
        token = create_access_token(
            user_id=1,
            role="user",
            expires_delta=expires_delta
        )
        payload = decode_token(token)
        
        # Проверка, что exp > iat
        assert payload["exp"] > payload["iat"]
        
        # Проверка, что разница примерно 30 минут (±10 секунд)
        time_diff = payload["exp"] - payload["iat"]
        expected_diff = 30 * 60  # 30 минут в секундах
        assert abs(time_diff - expected_diff) < 10


class TestJWTDecoding:
    """Тесты декодирования JWT"""
    
    def test_decode_valid_token(self):
        """Тест: валидный токен декодируется"""
        token = create_access_token(user_id=1, role="user")
        payload = decode_token(token)
        
        assert payload is not None
        assert "sub" in payload
    
    def test_decode_expired_token_raises_error(self):
        """Тест: истёкший токен вызывает ошибку"""
        from jose import JWTError
        
        # Создание токен с истекшим временем
        expired_payload = {
            "sub": "123",
            "role": "user",
            "iat": datetime.utcnow() - timedelta(hours=2),
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALG
        )
        
        # Должна возникнуть ошибка
        with pytest.raises(JWTError):
            decode_token(expired_token)
    
    def test_decode_invalid_signature(self):
        """Тест: токен с неверной подписью вызывает ошибку"""
        from jose import JWTError
        
        # Создание токена с неправильным секретом
        payload = {
            "sub": "123",
            "role": "user",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        invalid_token = jwt.encode(
            payload,
            "wrong_secret_key",
            algorithm=settings.JWT_ALG
        )
        
        # Должна возникнуть ошибка
        with pytest.raises(JWTError):
            decode_token(invalid_token)
    
    def test_decode_malformed_token(self):
        """Тест: некорректный токен вызывает ошибку"""
        from jose import JWTError
        
        malformed_token = "this.is.not.a.valid.jwt.token"
        
        with pytest.raises(JWTError):
            decode_token(malformed_token)
            