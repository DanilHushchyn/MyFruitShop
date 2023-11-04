# Generated by Django 4.2.6 on 2023-10-28 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0005_bank_alter_chatmessage_table_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fruitstorage',
            old_name='balance',
            new_name='amount',
        ),
        migrations.AddField(
            model_name='fruitstorage',
            name='name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.CreateModel(
            name='OperationJournal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('fruit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='admin_panel.fruitstorage')),
            ],
            options={
                'db_table': 'operation_journal',
            },
        ),
    ]
