# Generated by Django 4.2.6 on 2023-10-27 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0004_fruitstorage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.PositiveBigIntegerField(default=0)),
            ],
            options={
                'db_table': 'bank',
            },
        ),
        migrations.AlterModelTable(
            name='chatmessage',
            table='chat_message',
        ),
        migrations.AlterModelTable(
            name='fruitstorage',
            table='fruit_storage',
        ),
        migrations.AlterModelTable(
            name='room',
            table='room',
        ),
    ]
