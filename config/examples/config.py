"""
This is an example config file for our text mining project
It works as is and you should use it as is.

To use:
Copy this file into the config directory and you're done.
The copy in the config directory will be ignored by git and
will be safe for passwords
"""

from os import path


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(path.dirname(path.dirname(__file__)), 'db.sqlite3'),
    }
}

SECRET_KEY = 'this_is_secret!'

DATA_PATH = "path_to_wiki_data"

RELIGION_PATH = "path_to_religion_file"

PEOPLE_PATH = "path_to_people"

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         "NAME": 'postgres',
#         'USER': 'server',
#         'PASSWORD': 'password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#         }
# }
