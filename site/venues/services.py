import googlemaps
from django.conf import settings


def get_gmaps_place(place_id):
    '''Given a gmaps place_id, get the place's details and return.'''
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_PLACE_KEY)
    query = gmaps.place(place_id)
    if query['status'] == 'OK':
        return query['result']
    else:
        return False


def search_gmaps_place(query):
    '''Given a query string, usually the name of the Pub, search the
    gmaps API within 50,000 meters of Melbourne and return the results.'''
    radius = 50000
    lat_long = (-37.813611, 144.963056)
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_PLACE_KEY)
    query = gmaps.places(query, location=lat_long, radius=radius)
    if query['status'] == 'OK':
        return query['results']
    else:
        return False


def get_gmaps_image(photo_reference):
    '''Given a photo refernce ID, query the
    gmaps API and return raw photo data'''
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_PLACE_KEY)
    query = gmaps.places_photo(
        photo_reference,
        max_width=2000,
        max_height=2000)
    return query
