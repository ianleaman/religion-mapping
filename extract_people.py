'''
birth_date
birth_place
death_date
death_place
religion
party
'''

import bz2
import re
import sys
import re
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


def extract_box_date(line, subject=None):
    '''
    :params:
        :line: the string containing the line with the date
    '''
    print(line)

    return None


class person_info_box:
    '''
    Defines a person info box container.
    '''
    re_birth_date = re.compile("\|*.birth_date.*=")
    re_birth_place = re.compile("\|*.birth_place.*=")
    re_death_date = re.compile("\|*.death_date.*=")
    re_death_place = re.compile("\|*.death_place.*=")
    re_religion = re.compile("\|*.religion.*=")
    re_party = re.compile("\|*.party.*=")

    def __init__(self):
        self.boxText = ""
        self.subject = None
        self.birth_date = None
        self.birth_place = None
        self.death_date = None
        self.death_place = None
        self.religion = None
        self.party = None

    def addLine(self, line):
        self.boxText += line
        if person_info_box.re_birth_date.search(line):
            self.birth_date = extract_box_date(line.split("=", 1)[1])

        elif person_info_box.re_birth_place.search(line):
            self.birth_place = None

        elif person_info_box.re_death_date.search(line):
            self.death_date = extract_box_date(line.split("=", 1)[1])

        elif person_info_box.re_death_place.search(line):
            self.death_place = None

        elif person_info_box.re_religion.search(line):
            self.religion = None

        elif person_info_box.re_party.search(line):
            self.party = None

        elif "{{Infobox" in line:
            subject = extractBoxSubject(line)
            if subject:
                self.subject = subject

    def close(self):
        '''
        closes a box by tying up by saving it to the databse
        and linking the person with the db

        :return: none
        :accepts: none
        :raises: boxInvalidError
        '''
        # print(self.subject)
        pass
        # raise Exception("Close unimplemented")


onDoc = 0
brackLevel = 0
onPage = False
onInfoBox = False
box = ""
bracketSum = 0
box = None
i = 0
for line in f:
    line = line.decode("utf-8")
    if '<page>' in line:
        onPage = True
    elif '</page>' in line:
        onPage = False
    if onPage:
        if "{{Infobox" in line:
            box = person_info_box()
            bracketSum = 0
            onInfoBox = True

        if onInfoBox:
            bracketSum += line.count("{{") - line.count("}}")
            box.addLine(line)
            # Exit the infobox
            if bracketSum == 0:
                box.close()
                onInfoBox = False
                i += 1
            # Error Checking
            elif brackLevel < 0:
                raise Exception("Something went wrong in "
                                "finding the end of an infobox")

f.close()
