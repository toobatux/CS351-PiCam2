# Generated by Django 4.2.11 on 2024-04-17 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alerts_alertdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alerts',
            name='alertEndTime',
            field=models.TimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='alerts',
            name='alertStartTime',
            field=models.TimeField(auto_now_add=True),
        ),
    ]
