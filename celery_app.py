from celery import Celery


celery_app = Celery(
    main="aviso",
    broker="redis://localhost:6379/0"
)

