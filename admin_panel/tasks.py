import json
import random
import time

import httpx
from asgiref.sync import async_to_sync
from celery import current_task
from channels.layers import get_channel_layer

from MyFruitShop.celery import app
from admin_panel import models


@app.task(bind=True)
def fruits_trading(self, name, start, end, status):
    fruit = models.FruitStorage.objects.get(name=name)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'store_store',
        {
            'type': 'receive',
            'crontab': True,
            'status': status,
            'id': fruit.id,
            'amount': random.randint(start, end),
        }
    )


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(6.0, fruits_trading.s('яблоки', 1, 10, 'buy'), name='buy every 6 apple')
    sender.add_periodic_task(9.0, fruits_trading.s('бананы', 10, 20, 'buy'), name='buy every 9 banana')
    sender.add_periodic_task(12.0, fruits_trading.s('ананасы', 1, 10, 'buy'), name='buy every 12 pineapple')
    sender.add_periodic_task(15.0, fruits_trading.s('персики', 5, 15, 'buy'), name='buy every 15 peach')

    sender.add_periodic_task(15.0, fruits_trading.s('яблоки', 1, 10, 'sell'), name='sell every 6 apple')
    sender.add_periodic_task(12.0, fruits_trading.s('бананы', 1, 30, 'sell'), name='sell every 9 banana')
    sender.add_periodic_task(9.0, fruits_trading.s('ананасы', 1, 10, 'sell'), name='sell every 12 pineapple')
    sender.add_periodic_task(6.0, fruits_trading.s('персики', 1, 20, 'sell'), name='sell every 15 peach')


@app.task(bind=True)
def joke(self):
    response = httpx.get('https://v2.jokeapi.dev/joke/Any?type=single')
    joke = response.json().get('joke')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'chat_chat',
        {
            "type": "chat_message",
            "message": joke,

        }
    )


@app.task(bind=True)
def account_audit(self):
    channel_layer = get_channel_layer()
    for i in range(1, 16):
        time.sleep(1)
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': 15})

        async_to_sync(channel_layer.group_send)(
            'bank_bank',
            {
                "type": "progress",
                "progress_percent": (i * 100) / 15,

            }
        )
    return {'current': 100, 'total': 100}
