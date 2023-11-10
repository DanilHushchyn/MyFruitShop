import json

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import django
from datetime import datetime

from django.core.cache import cache

django.setup()

from .models import ChatMessage, FruitStorage, Bank, OperationJournal, Declaration
import admin_panel.tasks as tasks
from datetime import timedelta


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'chat'
        self.room_group_name = "chat_%s" % self.room_name
        self.user = self.scope["user"]

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        message = ChatMessage.objects.create(
            user_id=self.user.id if self.user.is_authenticated else 35,
            content=message
        )
        ChatMessage.objects.last().delete()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat.msg", "message": {
                'content': message.content,
                'user': message.user.last_name + message.user.first_name,
                'timestamp': message.timestamp.isoformat(),
            }}
        )

    def chat_msg(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"message": message}, sort_keys=True, default=str))


class BalanceConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'balance'
        self.room_group_name = "balance_%s" % self.room_name
        self.user = self.scope["user"]

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        amount = int(text_data_json['amount'])
        status = text_data_json['status']
        bank = Bank.objects.first()
        if status == 'minus':
            if bank.balance < amount:
                message = f'Ошибка: не удалось вывести {amount} usd'
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name, {
                        "type": "balance.operation", "data":
                            {
                                'status': False,
                                'message': message
                            }
                    }
                )
                return
            bank.balance = bank.balance - amount
            message = f'Успешно выведено {amount} usd'

        else:
            bank.balance = bank.balance + amount
            message = f'Успешно пополнено на {amount} usd'

        bank.save()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "balance.operation", "data":
                    {
                        'status': True,
                        'balance': bank.balance,
                        'message': message
                    }
            }
        )

    def balance_operation(self, event):
        data = event["data"]
        self.send(text_data=json.dumps(data, sort_keys=True, default=str))


class AuditConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.room_name = 'audit_%s' % self.user.id
        self.room_group_name = "accounting_%s" % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        if cache.get(f'user_{self.user.id}') is None:
            cache.set(f'user_{self.user.id}', 1)
            tasks.account_audit.delay(self.user.id)
        else:
            self.send(text_data=json.dumps({
                'status': False
            }, sort_keys=True, default=str))

    def progress(self, text_data):
        self.send(text_data=json.dumps({
            'percent': text_data['progress_percent']
        }, sort_keys=True, default=str))


class StoreConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'store'
        self.room_group_name = "store_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        if not isinstance(text_data, dict):
            text_data = json.loads(text_data)
        fruit_id = int(text_data['id'])
        fruit_amount = int(float(text_data['amount']))
        fruit = FruitStorage.objects.get(pk=fruit_id)
        bank = Bank.objects.first()
        total = fruit_amount * fruit.price
        today = datetime.today()
        count = Declaration.objects.filter(timestamp__day=today.day, timestamp__month=today.month,
                                           timestamp__year=today.year).count()
        if ((text_data['status'] == 'buy' and total > bank.balance) or
                (text_data['status'] == 'sell' and fruit_amount > fruit.amount)):
            operation = OperationJournal.objects.create(
                status='ERROR',
                type=text_data['status'],
                amount=fruit_amount,
                total_price=total,
                fruit_id=fruit_id,
            )
            OperationJournal.objects.last().delete()
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {
                    "type": "store.operation", "data":
                        {
                            'operation': {
                                "status": 'ERROR',
                                "fruit_id": fruit_id,
                                'timestamp': f'{operation.timestamp + timedelta(hours=2):%d-%m-%y %H:%M}',
                                'message': str(operation),
                            },
                            "crontab": text_data['crontab'],
                            "count": count,
                        }
                }
            )
            return
        bank.balance = bank.balance - total if text_data['status'] == 'buy' else bank.balance + total
        fruit.amount = fruit.amount + fruit_amount if text_data['status'] == 'buy' else fruit.amount - fruit_amount
        operation = OperationJournal.objects.create(
            status='SUCCESS',
            type=text_data['status'],
            amount=fruit_amount,
            total_price=total,
            fruit_id=fruit_id,
        )
        OperationJournal.objects.last().delete()
        bank.save()
        fruit.save()
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "store.operation", "data":
                    {
                        'balance': bank.balance,
                        'amount': fruit.amount,
                        'operation': {
                            "status": operation.status,
                            "fruit_id": fruit_id,
                            'timestamp': f'{operation.timestamp + timedelta(hours=2):%d-%m-%y %H:%M}',
                            'message': str(operation),
                        },
                        "crontab": text_data['crontab'],
                        "count": count,
                    }
            }
        )

    def store_operation(self, event):
        data = event["data"]
        self.send(text_data=json.dumps(data, sort_keys=True, default=str))
