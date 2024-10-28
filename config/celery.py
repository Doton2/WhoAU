import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


app.conf.timezone = 'Asia/Seoul'

#주기적으로 동작하게 작성
app.conf.beat_schedule = {
    "no-activate-delete": {
        "task": "chat.tasks.task_group_delete",
        "schedule": crontab(minute='*/5')
    }
}