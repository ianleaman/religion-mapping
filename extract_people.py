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

Notes:
    - Currently only assign one location to a person which is false,
      can have multiple

'''
import bz2
import re
import sys
import re
import json
from time import sleep
from django.db import IntegrityError
from geopy.geocoders import Nominatim

import traceback


from schema.models import *

sys.path.append('..')


f = bz2.open("data\enwiki-20150304-pages-articles-multistream.xml.bz2")


geolocator = Nominatim()
# Create a geographic buffer to reduce network calls
geo_dict = {}


# #######################################################
#
#                   Helper Functions
#
# #######################################################
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


def get_geocoords(place_list):
    coords = None
    # print(place_list)
    try:
        for place in place_list:
            if place in geo_dict:
                coords = geo_dict[place]
            else:
                coords = geolocator.geocode(place, timeout=30)
                sleep(.1)
                # coords = 10
                if coords:
                    geo_dict[place] = coords
                    break
    except GeocoderTimedOut:
        sleep(5)
        raise person_info_box.InvalidGeoTag
    except GeocoderServiceError:
        raise person_info_box.InvalidGeoTag

    # print(coords, coords.latitude, coords.longitude)
    # print("===")
    # coords = None
    if coords:
        return coords.latitude, coords.longitude
        # return "10.1", "10"
    else:
        return None, None


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
    re_birth_date = re.compile("\| *birth_date *=")
    re_birth_place = re.compile("\| *birth_place *=")
    re_death_date = re.compile("\| *death_date *=")
    re_death_place = re.compile("\| *death_place *=")
    re_religion = re.compile("\| *religion *=")
    re_party = re.compile("\| *party *=")

    class InvalidBox(Exception):
        pass

    class InvalidGeoTag(Exception):
        pass

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
            subject = self.subject
            birth_year = self.birth_date
            places = []

            # Prioritize death place over birth place
            if self.death_place:
                for place in self.death_place:
                    places.append(place)
            if self.birth_place:
                for place in self.birth_place:
                    places.append(place)

            death_year = self.death_date
            # Change these two to pickle fields?
            religion = json.dumps(self.religion)
            party = json.dumps(self.party)

            lat, lon = get_geocoords(places)
            loc = None
            # print(lat, lon)
            if lat and lon:
                loc = Location(lat=lat, lon=lon)
            else:
                raise person_info_box.InvalidGeoTag()

            person = Person(subject=subject, birth_year=birth_year,
                            death_year=death_year, religion=religion,
                            party=party)
            loc.save()
            person.save()
            person.places = [loc]
            person.save()
            # print(geolocator.geocode)
            # person = Person(**)
        else:
            # print("Invalid Loop")
            raise person_info_box.InvalidBox()
            pass
            # TODO: raise boxInvalidError()

    def _isValid(self):
        return (self.religion and (self.birth_place or self.death_place) and
                (self.birth_date or self.death_date))

    def _isValidWithLoc(self):
        return


onDoc = 0
brackLevel = 0
onPage = False
onInfoBox = False
box = ""
bracketSum = 0
box = None
# Box Counter
i = 0
# Keep track of last Boxes
lastBox = 348337

# numValid = 0
# numInValid = 0
# numGeoInvalid = 0
# Input previous stats
numValid = 8580
numInValid = 339615
numGeoInvalid = 142
try:
    for line in f:
        # A way to resume from abrupt stops
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
                try:
                    box.addLine(line)
                except TypeError:
                    continue
                # Exit the infobox
                if bracketSum == 0:
                    if i < lastBox:
                        pass
                    else:
                        try:
                            box.close()
                            numValid += 1
                        except UnicodeDecodeError:
                            print("error decode")
                        except UnicodeEncodeError:
                            print("error encode")
                        except person_info_box.InvalidBox:
                            numInValid += 1
                        except person_info_box.InvalidGeoTag:
                            numGeoInvalid += 1
                        except IntegrityError:
                            numInValid += 1

                    onInfoBox = False
                    i += 1

                    # Progress Report
                    if i % 1000 == 0:
                        if i < lastBox:
                            print("Skipped: ", end="")
                        print("Boxes Scanned: [", i, "] [", numValid, "/",
                              numInValid, "/", numGeoInvalid, "]")
                        sleep(2)

                    # if i >= 101:
                    #     break
                # Error Checking
                elif brackLevel < 0:
                    raise Exception("Something went wrong in "
                                    "finding the end of an infobox")
except Exception as e:
    print(e)
    traceback.print_exc()
    print("\n\nLast Box:", i, "\n\n")

print("Total Boxes Scanned: [", i, "] Valid: [", numValid, "/ Invalid:",
      numInValid, "/ Invalid Geo:", numGeoInvalid, "]")

f.close()

'''
Stats:
    Total Boxes Scanned: 2628531
    Valid Person Boxes: 28700
    Invalid boxes: 2599132
    Person Boxes with invalid Geo: 699
'''
