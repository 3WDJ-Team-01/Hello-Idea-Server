# Generated by Django 2.1.5 on 2019-04-23 13:23

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20190419_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='user_id',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='idea',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 23, 13, 23, 8, 367520, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 23, 13, 23, 8, 364499, tzinfo=utc)),
        ),
    ]