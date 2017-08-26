from venues.models import VenueDetails, OpenHours, VenueImage
from venues.utilities import get_and_write_image
from venues.services import search_gmaps_place, get_gmaps_place


# signal picks up model save here
def populate_venue(sender, **kwargs):
    '''Signal method for populating the models related to VenuePage'''
    instance = kwargs['instance']
    place_id = search_gmaps_place(instance.title)[0]['place_id']
    if place_id:
        place = get_gmaps_place(place_id)

    if place:
        venue = VenueDetails.objects.create_venue(instance, place)

        for day in place['opening_hours']['periods']:
            OpenHours.objects.create_openhours(venue, day)

        label_num = 0
        for photo in place['photos'][:6]:
            name = place['place_id'] + str(label_num)
            label_num += 1
            label = get_and_write_image(photo['photo_reference'], name)
            VenueImage.objects.create_venueimage(venue, label)


def remove_image(sender, **kwargs):
    '''Signal method for removing downloaded
    images after parent model is removed.'''
    instance = kwargs['instance']
    storage = instance.photo.storage
    path = instance.photo.path
    storage.delete(path)
