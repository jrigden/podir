# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-25 16:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0017_auto_20161025_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='subtitle',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='episode',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
    ]
