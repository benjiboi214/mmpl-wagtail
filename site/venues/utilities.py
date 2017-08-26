import os
from django.conf import settings
from venues.services import get_gmaps_image


def get_and_write_image(photo_reference, name):
    '''Given a photo reference and filepath for the image, get data from gmaps
    and write the file to the media directory for eventual storage in django
    model. Return the file name for use in the parent function.'''
    gmaps_path = 'gmaps_images'
    extension = '.jpeg'
    filename = name + extension
    label = os.path.join(gmaps_path, filename)

    if os.path.exists(os.path.join(settings.MEDIA_ROOT, label)):
        return label
    else:
        image = get_gmaps_image(photo_reference)
        with open(os.path.join(settings.MEDIA_ROOT, label), 'wb') as work:
            for chunk in image:
                if chunk:
                    work.write(chunk)
            work.close()
        return label
