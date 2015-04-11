
How this folder works (read it, its important!):

1. Files in the config folder named 'config.py' or '*-seeds.json' will be ignored.

2. Copy the config.py file from config/examples into the config folder to use it.
    The copy will be ignored and can contain passwords

This step not nessisary for now.
3. Copy the user-seeds.json file from config/examples into the config folder. The copy
    will be ignored and you can edit the copy as you wish. The current version will
    seed a dummy account with the password 'password'. It is perfectly good for
    development. After you do your initial migration, run:

    `python manage.py loaddata config/user-seeds.json`

    to add the development user to your database.

Configuration Originally Taken From Mimir Webserver