from __future__ import absolute_import, unicode_literals
import os

from .base import *

DEBUG = False


ALLOWED_HOSTS = ['beta.mmpl.org.au', 'mmpl.org.au', '188.166.221.96']


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = '/media/mmpl/development/static'
MEDIA_ROOT = '/media/mmpl/development/media'


try:
    from .production_secrets import *
except ImportError:
    pass
