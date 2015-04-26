'''
Jason Krone and Ian Leaman
'''

from django.conf import settings as django_settings

if not django_settings.configured:
    # ########### Initialize DB for use #########################
    from config import config
    import django
    django_settings.configure(DATABASES=config.DATABASES,
                              INSTALLED_APPS=("schema", ), DEBUG=False)
    django.setup()
    # End Initialize

from django.db import models


class Loc_Name(models.Model):
    name = models.CharField(max_length=1028, db_index=True)
    name_type = models.CharField(max_length=1028)
    location = models.ForeignKey('Location')


class Location(models.Model):
    """docstring for ClassName"""
    lon = models.DecimalField(max_digits=8, decimal_places=3)
    lat = models.DecimalField(max_digits=8, decimal_places=3)


class Person(models.Model):
    """docstring for ClassName"""
    subject = models.TextField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    places = models.ManyToManyField('Location')
    death_year = models.IntegerField(null=True, blank=True)
    # Change these two to pickle fields?
    religion = models.TextField()
    party = models.TextField(null=True, blank=True)
    # location = models.ForeignKey('Location')
