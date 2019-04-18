# Generated by Django 2.1.5 on 2019-04-18 05:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20190418_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword_log',
            name='keyword',
            field=models.CharField(default='None', max_length=50),
        ),
        migrations.AlterField(
            model_name='idea',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 18, 5, 37, 44, 256831, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 18, 5, 37, 44, 255835, tzinfo=utc)),
        ),
    ]
