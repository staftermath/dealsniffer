# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-07 03:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20170506_0152'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publisher',
            options={'ordering': ['-name']},
        ),
        migrations.AddField(
            model_name='book',
            name='num_pages',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
