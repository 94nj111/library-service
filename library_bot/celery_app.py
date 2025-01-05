from celery import Celery
from dotenv import load_dotenv

load_dotenv()

app = Celery("library_bot")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
