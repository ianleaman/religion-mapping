# ########### Initialize DB for use #########################
from django.conf import settings as django_settings
import django
django_settings.configure(DATABASES=config.DATABASES,
                          INSTALLED_APPS=("mimir_schema", ), DEBUG=False)
django.setup()
# End Initialize
