# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schema', '0002_auto_20150416_2041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='birth_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='death_year',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='party',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='subject',
            field=models.TextField(blank=True, null=True),
        ),
    ]
