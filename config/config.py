"""
This is an example config file for the
It works as is and you should use it as is (in development only)
if you have no problems.

To use:
Copy this file into the config directory and you're done.
The copy in the config directory will be ignored by git and
will be safe for passwords
"""

from os import path

# DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(path.dirname(path.dirname(__file__)), 'db.sqlite3'),
    }
}


SECRET_KEY = 'bnkanlxl&j31%zge2=q-pu1(!q0rl)4_--acl=di)2%-9)j_2_'

DATA_PATH = '/Users/jasonkrone/Developer/text_mining/'

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
