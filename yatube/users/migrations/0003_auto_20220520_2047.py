# Generated by Django 2.2.6 on 2022-05-20 17:47

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_contact_last_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='last_login',
            field=models.DateTimeField(
                default=datetime.datetime(
                    2022, 5, 20, 17, 47, 45, 664769, tzinfo=utc)),
        ),
    ]
