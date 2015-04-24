# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Loc_Name',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=1028)),
                ('name_type', models.CharField(max_length=1028)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lon', models.DecimalField(max_digits=8, decimal_places=3)),
                ('lat', models.DecimalField(max_digits=8, decimal_places=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.TextField()),
                ('birth_year', models.IntegerField()),
                ('death_year', models.IntegerField()),
                ('religion', models.TextField()),
                ('party', models.TextField()),
                ('birth_place', models.ManyToManyField(to='schema.Location')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='loc_name',
            name='location',
            field=models.ForeignKey(to='schema.Location'),
            preserve_default=True,
        ),
    ]
