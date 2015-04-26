import os
import sys
sys.path.append('..')
# Requires at least debug, and secret key from django_settings
# from config import django_settings
from config import config


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASES = config.DATABASES

SECRET_KEY = config.SECRET_KEY


INSTALLED_APPS = (
    'schema',
)


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
