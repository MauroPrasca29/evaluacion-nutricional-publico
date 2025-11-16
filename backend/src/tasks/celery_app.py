from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "anemia_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
)

# Importar explícitamente las tareas para que el worker las registre al iniciar
try:
    import tasks.anemia_tasks  # noqa: F401
except Exception:
    pass
