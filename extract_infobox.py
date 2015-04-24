import bz2
import re
import sys
sys.path.append('..')

f = bz2.open("data\enwiki-20150304-pages-articles-multistream.xml.bz2")


# TODO: Move this to seperate func
# ########### Initialize DB for use #########################
from config import config
from django.conf import settings as django_settings
import django
django_settings.configure(DATABASES=config.DATABASES,
                          INSTALLED_APPS=("schema", ), DEBUG=False)
django.setup()
# End Initialize


def extractBoxSubject(boxHeader):
    postIbox = boxHeader.split("{{Infobox", 1)[-1]
    subject = re.split("&|\||{|{{", postIbox, 1)[0]
    return subject.strip().lower()


onDoc = 0
brackLevel = 0
onPage = False
onInfoBox = False
box = ""
bracketSum = 0
i = 0
for line in f:
    line = line.decode("utf-8")
    if '<page>' in line:
        onPage = True
    elif '</page>' in line:
        onPage = False
    if onPage:
        if "{{Infobox" in line:  # TODO: may have spaces... ect
            bracketSum = 0
            box = ""
            onInfoBox = True
            # Spin off to function extract_box_subject
            # + account for other cases
            boxSubject = extractBoxSubject(line)
            if boxSubject:
                # print(boxSubject)
                pass
            else:
                # TODO: ignore if this occurs or get next line
                print(line)
                print("ERRROR")
            # Skip info box subject and move on to processing
            # The next line
            # continue

        if onInfoBox:
            bracketSum += line.count("{{") - line.count("}}")
            box += line
            # Exit the infobox
            if bracketSum == 0:
                # print(box.encode("utf-8"))
                onInfoBox = False
                i += 1
            # Error Checking
            elif brackLevel < 0:
                raise Exception("Something went wrong in "
                                "finding the end of an infobox")

f.close()
