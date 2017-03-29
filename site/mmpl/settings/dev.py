from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'jm+*bj5!z(wbj@b23qaha65a$tro150+vx+mobvpg%2!tdzu^j'

# Add here on down to production file.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.mmpl.org.au'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'thestatistician@mmpl.org.au'
# EMAIL_HOST_PASSWORD =
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_SUBJECT_PREFIX = '[Wagtail] '

WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = EMAIL_HOST_USER

try:
    from .local import *
except ImportError:
    pass
