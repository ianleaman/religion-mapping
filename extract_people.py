'''
birth_date
birth_place
death_date
death_place
religion
party


TODO:
    - how should we best track errors?
    - build religion list while processing
    - when trying to determin places give more weights to palces where more
        locs appear?
    - refactor get_box_location and get_box_religion


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


# #######################################################
#
#                   Helper Functions
#
# #######################################################
def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def find_between(s, first, last):
    '''
    Returns the first occurence of the substring in s that occurs
    between the strings first and last.
    :params:
        :s: The full string to search
        :first: The starting character to check
        :last: The ending character to check
    '''
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def find_all_between(s, first, last):
    '''
    Returns the all the occurences of the substrings in s that occur
    between the strings first and last.
    :params:
        :s: The full string to search
        :first: The starting character to check
        :last: The ending character to check
    '''
    occurences = []
    while not len(s) == 0:
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            occurences.append(s[start:end])
            s = s[end:]
        except ValueError:
            break

    if not occurences:
        return None

    return occurences


def find_between_test():
    pass


def find_all_between_test():
    test_str = "[[bet (letter)|bet]]-[[ayin]]-[[lamedh]]"
    l = find_all_between(test_str, "[[", "]]")
    if not len(l) == 2:
        print("Test Failed")

    test_str2 = "[[some text]]"
    test_str3 = "[[some text}}"
    test_str4 = "a"
# #######################################################
#
#                   End Helper Functions
#
# #######################################################


def extractBoxSubject(boxHeader):
    postIbox = boxHeader.split("{{Infobox", 1)[-1]
    subject = re.split("&|\||{|{{", postIbox, 1)[0]

    return subject.strip().lower()


def extract_box_date(line, subject=None):
    '''
    :params:
        :line: the string containing the line with the date
    '''
    year = None
    line = line.strip()
    # Check case one
    if ("{{" in line) and ("}}" in line):
        linesplit = line.strip("}").strip("{").split("|")
        # print(linesplit)
        for entry in linesplit:
            if isInt(entry):
                year = int(entry)
                break

    return year


def extract_line_links(line):
    '''
    cases:
        1) just place name
        2) [[link]]
        3) [[link | link]]
        4) [[link]] some text [[link]]

    '''
    final_links = []
    if "[[" in line:
        for entry in find_all_between(line, "[[", "]]"):
            # Split along the sub catagories
            for final in entry.split("|"):
                final_links.append(final)
    else:
        line = line.strip()
        # Checks if there is a valid country, if not return none rather than
        # an empty list
        if line:
            final_links.append(line)
        else:
            return None

    return final_links


def get_val(line):
    '''
    accepts a line and returns the value after the equals sign
    '''
    return line.split("=", 1)[1]


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
            self.birth_date = extract_box_date(get_val(line))

        elif person_info_box.re_birth_place.search(line):
            self.birth_place = extract_line_links(get_val(line))

        elif person_info_box.re_death_date.search(line):
            self.death_date = extract_box_date(get_val(line))

        elif person_info_box.re_death_place.search(line):
            self.death_place = extract_line_links(get_val(line))

        elif person_info_box.re_religion.search(line):
            self.religion = extract_line_links(get_val(line))

        elif person_info_box.re_party.search(line):
            self.party = extract_line_links(get_val(line))

        elif "{{Infobox" in line:
            subject = extractBoxSubject(line)
            if subject:
                self.subject = subject

    def close(self):
        '''
        closes a box by saving it to the databse
        and linking the person with the db

        record what we throw out.

        :return: none
        :accepts: none
        :raises: boxInvalidError
        '''
        # Push out to box is valid function
        if self._isValid():
            # print([x.encode("utf-8") for x in self.birth_place])
            print(self.party)
            # pass
        else:
            pass
            # TODO: raise boxInvalidError()

    def _isValid(self):
        return (self.religion and (self.birth_place or self.death_place) and
                (self.birth_date or self.death_date))


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
        onInfoBox = False  # Is this nessiary
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
