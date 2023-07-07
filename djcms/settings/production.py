from .base import *

from distutils.util import strtobool

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = strtobool(os.environ['DEBUG'])

# Use comma , to insert multiple host in env
ALLOWED_HOSTS = [host.strip() for host in os.environ['HOSTS'].split(',')]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.environ['SQLITE_PATH'],
    }
}

STATIC_ROOT = os.environ['STATIC_ROOT']

MEDIA_ROOT = os.environ['MEDIA_ROOT']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
