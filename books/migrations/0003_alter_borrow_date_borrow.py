# Generated by Django 3.2.13 on 2022-06-10 02:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20220609_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='borrow',
            name='date_borrow',
            field=models.DateField(default=datetime.datetime.today, verbose_name='Date borrow'),
        ),
    ]
