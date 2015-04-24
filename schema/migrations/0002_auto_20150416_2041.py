# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schema', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='birth_place',
            new_name='places',
        ),
    ]
