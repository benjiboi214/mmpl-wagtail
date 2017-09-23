from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import pre_delete
from wagtail.wagtailcore.signals import page_published


class VenuesConfig(AppConfig):
    '''Config method for naming app and registering signals.'''
    name = 'venues'

    def ready(self):
        from home.models import VenuePage
        from venues.models import VenueImage
        from venues.signals import populate_venue, remove_image

        page_published.connect(populate_venue, sender=VenuePage)
        pre_delete.connect(remove_image, sender=VenueImage)
