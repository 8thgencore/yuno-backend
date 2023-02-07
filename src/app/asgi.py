from app.main import create_application

app = create_application()
celery = app.celery_app
