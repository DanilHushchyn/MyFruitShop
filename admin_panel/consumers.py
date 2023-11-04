import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import django
django.setup()

from .models import ChatMessage, FruitStorage, Bank, OperationJournal
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

        ChatMessage.objects.create(
            user_id=self.user.id if self.user.is_authenticated else 35,
            content=message
        )
        ChatMessage.objects.last().delete()
        messages = ChatMessage.objects.order_by('timestamp').values('user__first_name',
                                                                    'user__last_name',
                                                                    'content',
                                                                    'timestamp')

        self.send(text_data=json.dumps({
            'messages': list(messages)[::-1][:40][::-1]
        }, sort_keys=True, default=str))

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        ChatMessage.objects.create(
            user_id=33,
            content=message
        )
        ChatMessage.objects.last().delete()
        messages = ChatMessage.objects.order_by('timestamp').values('user__first_name',
                                                                    'user__last_name',
                                                                    'content',
                                                                    'timestamp')
        self.send(text_data=json.dumps({
            'messages': list(messages)[::-1][:40][::-1]
        }, sort_keys=True, default=str))


class BalanceConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        amount = int(text_data_json['amount'])
        status = text_data_json['status']
        bank = Bank.objects.first()
        if status == 'minus':
            if bank.balance < amount:
                message = f'Ошибка: не удалось вывести {amount} usd'
                self.send(text_data=json.dumps({
                    'status': False,
                    'message': message
                }, sort_keys=True, default=str))
                return
            bank.balance = bank.balance - amount
            message = f'Успешно выведено {amount} usd'

        else:
            bank.balance = bank.balance + amount
            message = f'Успешно пополнено на {amount} usd'

        bank.save()
        self.send(text_data=json.dumps({
            'status': True,
            'balance': bank.balance,
            'message': message
        }, sort_keys=True, default=str))


class AuditConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'bank'
        self.room_group_name = "bank_%s" % self.room_name

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
        tasks.account_audit.delay()

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
            self.send(text_data=json.dumps({
                'operation': {
                    "status": 'ERROR',
                    "fruit_id": fruit_id,
                    'timestamp': f'{operation.timestamp + timedelta(hours=2):%d-%m-%y %H:%M}',
                    'message': str(operation),
                },
                "crontab": text_data['crontab'],
            }, sort_keys=True, default=str))
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
        self.send(text_data=json.dumps({
            'balance': bank.balance,
            'amount': fruit.amount,
            'operation': {
                "status": operation.status,
                "fruit_id": fruit_id,
                'timestamp': f'{operation.timestamp + timedelta(hours=2):%d-%m-%y %H:%M}',
                'message': str(operation),
            },
            "crontab": text_data['crontab'],
        }, sort_keys=True, default=str))
