from celery import Celery

from app.core.config import settings

# Создание Celery приложения
celery_app = Celery(
    "bot_service",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.llm_tasks"]  # Указание модуля с задачами
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 минут на задачу
    task_soft_time_limit=240,  # Мягкий лимит 4 минуты
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks(["app.tasks"])
