# Generated by Django 4.2.6 on 2023-10-30 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0007_operationjournal_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='fruitstorage',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='operationjournal',
            name='name',
            field=models.CharField(choices=[('buy', 'buy'), ('sell', 'sell')], max_length=50, null=True),
        ),
    ]
