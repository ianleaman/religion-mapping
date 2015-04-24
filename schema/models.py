'''
Jason Krone and Ian Leaman
'''

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
    birth_place = models.ForeignKey('Location')
    death_year = models.IntegerField()
    death_place = models.ForeignKey('Location')
    religion = models.TextField()
    party = models.TextField()
