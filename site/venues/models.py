from __future__ import unicode_literals

from django.db import models
from home.models import VenuePage
import random


class VenueDetailsManager(models.Manager):
    def create_venue(self, venue_page, place):
        venue, created = self.update_or_create(venue_page=venue_page)
        try:
            venue.place_id = place['place_id']
        except:
            pass
        try:
            venue.address = place['formatted_address']
        except:
            pass
        try:
            venue.phone = place['formatted_phone_number']
        except:
            pass
        try:
            venue.website = place['website']
        except:
            pass
        try:
            venue.gmaps_url = place['url']
        except:
            pass
        venue.save()
        return venue


class VenueDetails(models.Model):
    '''Model for saving the venue's details once
    the venue name is saved in the VenuePage'''
    venue_page = models.OneToOneField(
        VenuePage,
        models.CASCADE,
        related_name='venue_details')
    place_id = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    website = models.CharField(max_length=100, blank=True)
    gmaps_url = models.CharField(max_length=100, blank=True)

    objects = VenueDetailsManager()


class OpenHoursManager(models.Manager):
    def create_openhours(self, venue, day):
        try: 
            open_hours_id = (str(day['open']['day']) + day['open']['time'] +
                            str(day['close']['day']) + day['close']['time'] +
                            random.randint(1,100000))
            open_hours, created = self.update_or_create(
                uuid=open_hours_id,
                venue=venue)
            open_hours.open_day = day['open']['day']
            open_hours.open_time = day['open']['time']
            open_hours.close_day = day['close']['day']
            open_hours.close_time = day['close']['time']
            open_hours.save()
        except KeyError:
            pass


class OpenHours(models.Model):
    '''Model for storing and processing Open Hours
    for presentation with the VenuePage model'''
    DAY_OF_WEEK_CHOICES = (
        ('0', 'Sunday'),
        ('1', 'Monday'),
        ('2', 'Tuesday'),
        ('3', 'Wednesday'),
        ('4', 'Thursday'),
        ('5', 'Friday'),
        ('6', 'Saturday'))
    uuid = models.CharField(max_length=20, primary_key=True)
    venue = models.ForeignKey(
        VenueDetails,
        related_name='openhours',
        on_delete=models.CASCADE)
    open_day = models.CharField(
        max_length=1,
        choices=DAY_OF_WEEK_CHOICES)
    open_time = models.CharField(max_length=10)
    close_day = models.CharField(
        max_length=1,
        choices=DAY_OF_WEEK_CHOICES)
    close_time = models.CharField(max_length=10)

    objects = OpenHoursManager()


class VenueImageManager(models.Manager):
    def create_venueimage(self, venue, label):
        venue_image = self.create(venue=venue)
        venue_image.photo = label
        venue_image.save()


class VenueImage(models.Model):
    '''Model for saving the Venue images'''
    photo = models.ImageField(
        upload_to='gmaps_images/',
        blank=True,
        max_length=300)
    venue = models.ForeignKey(
        VenueDetails,
        related_name='photos',
        on_delete=models.CASCADE
    )

    objects = VenueImageManager()
