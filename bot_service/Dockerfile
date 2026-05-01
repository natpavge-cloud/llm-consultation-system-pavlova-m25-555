FROM python:3.12-slim

# Установка переменных окружения
# PYTHONUNBUFFERED: заставляет логи выводиться сразу (важно для контейнеров)
# PYTHONDONTWRITEBYTECODE: не засоряет контейнер .pyc файлами
# UV_PROJECT_ENVIRONMENT: ставит пакеты в системный путь, чтобы не использовать venv внутри Docker
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

# Установка uv
RUN pip install --no-cache-dir uv

# Копирование файлов зависимостей
COPY pyproject.toml .
COPY uv.lock* .

# Установка зависимостей напрямую в систему (благодаря UV_PROJECT_ENVIRONMENT)
RUN uv sync --frozen --no-dev

# Копирование всего кода проекта
COPY . .

# По умолчанию запуск служебного FastAPI приложения (healthcheck)
# Поскольку пакеты в системе, можно вызывать uvicorn напрямую
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]