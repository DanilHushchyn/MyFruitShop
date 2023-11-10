import os
import random

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyFruitShop.settings')

app = Celery('MyFruitShop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_routes = {
    'admin_panel.tasks.joke': {'queue': 'celery'},
    'admin_panel.tasks.fruits_trading': {'queue': 'trading_queue'},
    'admin_panel.tasks.account_audit': {'queue': 'celery','concurrency': 4},
}

app.conf.beat_schedule = {
    'joke_in_chat_every_minute': {
        'task': 'admin_panel.tasks.joke',
        'schedule': 15.0
    },
}
app.conf.timezone = 'Europe/Kiev'
