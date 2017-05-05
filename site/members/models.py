from __future__ import unicode_literals
from datetime import date

from django.db import models

from address.models import AddressField


class Player(models.Model):
    '''Model for recording player related data. To start, covers all
    information included in the player registration form,'''
    ACCREDITATION_CHOICES = (
        ('A', 'A Grade'),
        ('B', 'B Grade'),
        ('C', 'C Grade'),
        ('D', 'D Grade'),
        ('N', 'None'),
    )

    firstname = models.CharField(max_length=64, verbose_name='First Name')
    lastname = models.CharField(max_length=64, verbose_name='Last Name')
    dob = models.DateField(verbose_name='Date of Birth')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=15, verbose_name='Phone Number')
    address = AddressField(related_name='player', verbose_name='Address')
    joined = models.DateField(default=date.today, verbose_name='Join Date')
    updated = models.DateField(auto_now=True, verbose_name='Last Updated')
    media_release = models.BooleanField(
        default=False,
        verbose_name='Media Release'
    )
    umpire_accreditation = models.CharField(
        max_length=1,
        choices=ACCREDITATION_CHOICES,
        default='N',
        verbose_name='Umpire Accreditation'
    )

    def unicode(self):
        return "%s %s" % (self.firstname, self.lastname)


class Notifications():
    '''Model for tracking notifications preferences for various parts of the
    website.'''
    player = models.OneToOneField(
        Player,
        on_delete=models.CASCADE,
        primary_key=True
    )
    events = models.BooleanField(default=True)
    results = models.BooleanField(default=True)
    resources = models.BooleanField(default=True)
    news = models.BooleanField(default=True)


class Venue(models.Model):
    '''Model for tracking Venues visited by the league. Contains all relevant
    information for contacting venue, as well as housing the number of
    tables available to be used in fixture generation.'''
    name = models.CharField(max_length=128)
    address = AddressField(related_name='venue', verbose_name='Address')
    tables = models.PositiveIntegerField(verbose_name='Number of Tables')
    models.CharField(max_length=15, verbose_name='Phone Number')
    contact_name = models.CharField(max_length=128, verbose_name='Contact Name')
    # Has hours of operation


class Committee(models.Model):
    '''Model for recording Committee membership. Creating a new entry per year
    for each new committee voted in will serve as a historical record of
    members service, as well as presenting current committee'''
    # Has a president __Player
    # Has a vice president __Player
    # Has a treasurer __Player
    # Has a statistician __Player
    # Has a secretary __Player
    # Has a asst secretary __Player
    # Has AGM date (inferring election date)
    # Has end date
    pass
