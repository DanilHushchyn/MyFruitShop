from django.db import models
from django.contrib.auth.models import User
import pymorphy2

from admin_panel.utilities import get_timestamp_path


class ChatMessage(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content} [{self.timestamp}]'

    class Meta:
        db_table = "chat_message"
        ordering = ['-timestamp',]


class FruitStorage(models.Model):
    name = models.CharField(max_length=50, null=True)
    amount = models.PositiveBigIntegerField(default=0)
    price = models.IntegerField(default=0)

    class Meta:
        db_table = "fruit_storage"
        ordering = ['id']


class OperationJournal(models.Model):
    OPERATION_CHOICES = (
        ('buy', 'buy'),
        ('sell', 'sell'),
    )
    type = models.CharField(max_length=10, choices=OPERATION_CHOICES, null=True)
    CHOICES = (
        ('SUCCESS', 'SUCCESS'),
        ('ERROR', 'ERROR'),
    )
    amount = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=CHOICES, null=True)
    fruit = models.ForeignKey(to=FruitStorage, related_name='operations', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.type == "buy":
            status = 'куплено' if self.status == 'SUCCESS' else 'не куплено'
        else:
            status = 'продано' if self.status == 'SUCCESS' else 'не продано'
        return f'{status} {self.amount} {self.fruit.name} за {self.total_price} usd'

    class Meta:
        db_table = "operation_journal"
        ordering = ['-timestamp']


class Bank(models.Model):
    balance = models.PositiveBigIntegerField(default=0)

    class Meta:
        db_table = "bank"


class Declaration(models.Model):
    file = models.FileField(verbose_name='', upload_to=get_timestamp_path)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "declaration"
