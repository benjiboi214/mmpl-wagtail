from __future__ import absolute_import, unicode_literals
import os

from .base import *

DEBUG = False


ALLOWED_HOSTS = [
    'production.bennyda.ninja',
    'mmpl.org.au',
    'www.mmpl.org.au',
]


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = '/media/mmpl/production/static'
MEDIA_ROOT = '/media/mmpl/production/media'


try:
    from .production_secrets import *
except ImportError:
    pass
