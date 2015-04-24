'''
Jason Krone and Ian Leaman
'''
if not django_settings.configured:
    # ########### Initialize DB for use #########################
    from config import config
    from django.conf import settings as django_settings
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
    subject = models.TextField()
    birth_year = models.IntegerField()
    places = models.ManyToManyField('Location')
    death_year = models.IntegerField()
    # Change these two to pickle fields?
    religion = models.TextField()
    party = models.TextField()
