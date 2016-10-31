# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0014_auto_20161025_0007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='podcast',
            name='author',
        ),
        migrations.AddField(
            model_name='podcast',
            name='active',
            field=models.BooleanField(db_index=True, default=True),
        ),
    ]