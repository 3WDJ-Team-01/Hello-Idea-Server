# Generated by Django 2.1.5 on 2019-04-23 14:28

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20190423_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='idea',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 23, 14, 28, 16, 372509, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 23, 14, 28, 16, 371510, tzinfo=utc)),
        ),
    ]
