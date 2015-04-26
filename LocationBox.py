import re
import sys
import bz2

from schema.models import Loc_Name, Location
from config import config

NAME_KEYS = {"en_name": re.compile("\| *en_name *="),
             "conventional_long_name": re.compile("\| *conventional_long_name *="),
             "official_name": re.compile("\| *official_name *="),
             "native_name": re.compile("\| *native_name *="),
             "other_name": re.compile("\| *other_name *="),
             "common_name": re.compile("\| *common_name *="),
             "name": re.compile("\| *name *=")
             }

LAT_LON_KEYS = {"latd": re.compile("\| *latd *="),
                "latm": re.compile("\| *latm *="),
                "lats": re.compile("\| *lats *="),
                "latns": re.compile("\| *latns *="),
                "longd": re.compile("\| *longd *="),
                "longm": re.compile("\| *longm *="),
                "longs": re.compile("\| *longs *="),
                "longew": re.compile("\| *longew *="),
                "lat": re.compile("\| *lat *="),
                "lon": re.compile("\| *lon *="),
                }

COORD_KEYS = {"coor": re.compile("\| *coor *="),
              "coord": re.compile("\| *coord *=")
              }


class InvalidBox(Exception):
    pass


def is_location(box):
    for latlon_key in LAT_LON_KEYS:
        if latlon_key in box:
            return True
    for coord_key in COORD_KEYS:
        if coord_key in box:
            return True
    return False


def add_loc(info_box):
    loc_dict = {}
    box_fields = info_box.split("\n")

    for line in box_fields:
        # extract name of location
        for name_key, regex in NAME_KEYS.items():
            if regex.search(line):
                loc_dict[name_key] = name_from_line(line)

        # extract lat/lon coords of location
        for latlon_key, regex in LAT_LON_KEYS.items():
            if regex.search(line):
                loc_dict[latlon_key] = latlon_for_key(latlon_key, line)

        # extract coordinate block
        for coord_key, regex in COORD_KEYS.items():
            if regex.search(line):
                cd = coord_dict(line)
                #  add items in coord dictionary to loc_dict
                loc_dict = merge_dicts(loc_dict, cd)

    latdd, londd = dd_coords(loc_dict)
    if latdd and londd and has_name(loc_dict):
        loc_dict["latdd"] = latdd
        loc_dict["londd"] = londd
        create_loc_obj(loc_dict)
    else:
        raise InvalidBox()

def test_add_loc():
    f = open('/Users/jasonkrone/Developer/text_mining/data/peru.txt', 'r')
    loc_box = ''
    for line in f:
        loc_box += line
    print("loc_box b4", loc_box)
    loc_box = latlon_format_fix(loc_box.lower())
    print("loc_box after", loc_box)
    add_loc(loc_box)

def merge_dicts(dict_a, dict_b):
    if dict_b is not None:
        for key, val in dict_b.items():
            dict_a[key] = val
    return dict_a

def create_loc_obj(loc):
    names = []
    location = Location.objects.get_or_create(lat=loc["latdd"], lon=loc["londd"])[0]
    for name_type in NAME_KEYS:
        name = loc.get(name_type)
        if name is not None:
            loc_name = Loc_Name(name=name, name_type=name_type, location=location)
            loc_name.save()


def has_name(loc_dict):
    has_name = False
    for name in NAME_KEYS:
        if loc_dict.get(name) is not None:
            has_name = True
            break
    return has_name

def dd_coords(loc_dict):
    latd = loc_dict.get("latd")
    latm = zero_if_none(loc_dict.get("latm"))
    lats = zero_if_none(loc_dict.get("lats"))
    latns = loc_dict.get("latns")

    longd = loc_dict.get("longd")
    longm = zero_if_none(loc_dict.get("longm"))
    longs = zero_if_none(loc_dict.get("longs"))
    longew = loc_dict.get("longew")

    if latd and longd and latns and longew:
        latdd = decimal_degrees(latd, latm, lats, latns)
        longdd = decimal_degrees(longd, longm, longs, longew)
        return latdd, longdd
    else:
        return None, None

def decimal_degrees(d, m, s, direction):
    dec_degrees = d + m/60.0 + s/3600.0
    if direction in ["s", "w"]:
        dec_degrees = dec_degrees * -1
    return dec_degrees

def zero_if_none(val):
    if val is None:
        return 0
    else:
        return val

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#                               EXTRACT NAMES                                 #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def name_from_line(line):
    name = None
    key_value = line.split("=", 1)
    if len(key_value) == 2:  # check that the line had both key and value
        dirty_name = key_value[1]
        name = re.split("&|\||{|{{", dirty_name, 1)[0]  # exclude nonsense
        name = name.strip()
    if name == "":
        name = None
    return name


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#                     EXTRACT COORDS WITH LAT LON KEYS                        #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def latlon_for_key(latlon_key, line):
    """
    returns the value under the given lat/lon key (ex. latd, latm, lats, latns)
    """
    latlon_for_key = None
    coord_array = filter(None, line.split("|"))  # bar separates keyvalue pairs
    coord_pairs = [pair.split("=") for pair in coord_array]

    for pair in coord_pairs:
        if len(pair) == 2:
            key = pair[0].strip()
            value = pair[1].strip()
            if key == latlon_key and is_coord_str(value):
                if key == "latns" or key == "longew":
                    latlon_for_key = value
                else:
                    latlon_for_key = float(value)
                break
    return latlon_for_key

def is_coord_str(coord):
    """
    returns True if the given string is a valid representation of a dms
    coordniate value or cardinal direction.  Otherwise, returns False
    """

    is_valid = False
    if coord in ["n", "s", "e", "w"]:
        is_valid = True
    elif is_numeric_str(coord):
        if -180 <= floatify(coord) and floatify(coord) <= 180:
            is_valid = True
    return is_valid

def is_numeric_str(val):
    """
    returns true if the given value is a numeric string and false otherwise
    """

    is_num_str = False
    if isinstance(val, str):
        try:
            num = float(val)
            is_num_str = True
        except ValueError:
            pass
    return is_num_str


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #
#                     EXTRACT LAT LON FROM COORD FORMAT                       #
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

LAT_KEYS = ["latd", "latm", "lats"]
LON_KEYS = ["longd", "longm", "longs"]

def coord_dict(line):
    """"
    creates a coordinate dictionary with keys: latd, latm, lats, latns, longd, longm, longs, longew
    from the given line
    """

    coord_dict = {}
    lats, lons = extract_lats_lons(line)
    if lats is not None and lons is not None:
        coord_dict = insert_vals_at_keys(coord_dict, LAT_KEYS, lats, is_float, "latns")
        coord_dict = insert_vals_at_keys(coord_dict, LON_KEYS, lons, is_float, "longew")
    else:
        coord_dict = None
    return coord_dict

def insert_vals_at_keys(a_dict, keys, vals, is_valid, invalid_key):
    """
    Inserts the given values under the given keys in the order they appear in
    the given lists if the values are vaild. If a value is not vaild, it is
    inserted into the dictionary under the invalid key. Modified dictionary is
    returned
    """

    key_iter = keys.__iter__()

    for val in vals:
        if is_valid(val):
            key = key_iter.__next__()
            a_dict[key] = val
        else:
            a_dict[invalid_key] = val
    return a_dict

def is_float(val):
    if isinstance(val, float):
        return True
    else:
        return False

def extract_lats_lons(line):
    """
    returns a tuple containing a list of the latitude values
    and longitude values in the given line if those values are present.
    Otherwise returns None.
    """

    lats = None
    lons = None
    coords = coord_vals_from_text(line)
    if coords is not None:
        length = len(coords)
        if length > 0 and length % 2 == 0:
            first_half = [floatify(coord) for coord in coords[0:int(length/2)]]
            second_half = [floatify(coord) for coord in coords[int(length/2):]]
            if "n" in first_half or "s" in first_half:
                lats = first_half
                lons = second_half
            elif "e" in first_half or "w" in first_half:
                lats = second_half
                lons = first_half
    return lats, lons

def coord_vals_from_text(line):
    """
    Returns a list of coordinate values in the given line, if the line contains
    valid coordinates.  Otherwise, returns None
    """

    coord_vals = None
    try:
        coord_text = re.search("{ *{ *coord(.*)\|", line).group(1)
    except AttributeError:
        return None
    # values are separated by |
    coords_dirty = coord_text.split("|")
    # get rid of lines filled with only spaces or empty sting
    coords_dirty = filter(None, [coord.strip() for coord in coords_dirty])
    coords_clean = [coord for coord in coords_dirty if is_coord_str(coord)]
    # convert strings to values
    coord_vals = [floatify(coord) for coord in coords_clean]
    if len(coord_vals) % 2 != 0:  # bad coord vals
        coord_vals = None
    return coord_vals

def floatify(val):
    """
    returns the given value cast as an float if no exception is thrown.
    Otherwise, returns given value
    """

    try:
        num = float(val)
        return num
    except ValueError:
        return val
























def test_coord_vals():
    line1 = "| coordinates {{Coord|0|40|S|90|33|W|scale:1400000|display=inline,title}}".lower()
    line2 = "|coor          ={{Coord|36|0|4|N|78|56|20|W|type:edu_region:US-NC|display=inline,title}}".lower()
    line3 = "| coordinates {{Coord|0|900|S|90|33|W|scale:1400000|display=inline,title}}".lower()

    coordv1 = coord_vals_from_text(line1)
    coordv2 = coord_vals_from_text(line2)
    coordv3 = coord_vals_from_text(line3)

    correctv1 = [0, 40, "s", 90, 33, "w"]
    correctv2 = [36, 0, 4, "n", 78, 56, 20, "w"]

    if coordv1 == correctv1:
        print("Test coordv1 Passed")
    else:
        print("Test coordv1 Failed coordv1:", coordv1, "not", correctv1)

    if coordv2 == correctv2:
        print("Test coordv2 Passed")
    else:
        print("Test coordv2 Failed coordv2:", coordv2, "not", correctv2)
    if coordv3 is None:
        print("Test coordv3 Passed")
    else:
        print("Test coordv3 Failed coordv3:", coordv3, "not", None)


def decimal_degrees_from_dms_test():
    """
    |latd=8 |latm= 32|latNS=S |longd=179 |longm=13 |longEW=E
    TODO: decide what to do with this
    """
    lat_string1 = "| latd = 51 | latm = 30 | lats = 26  | latNS = N"
    lon_string1 = "| longd = 0 | longm = 7 | longs = 39 | longEW = W"
    lat1_dd = decimal_degrees_from_dms(lat_string1)
    lon1_dd = decimal_degrees_from_dms(lon_string1)
    # lat test_!
    if lat1_dd is not None and abs(lat1_dd - 51.5072222) < 0.0001:
        print("lat1_test Passed")
    else:
        print("lat1: ", lat1_dd, "not", 51.5072222, "\n")
        print("lat1_test Failed")
    # lon test_1
    if lon1_dd is not None and abs(lon1_dd - 0.1275) < 0.0001:
        print("lon1_test Passed")
    else:
        print("lon1: ", lon1_dd, "not", 0.1275, "\n")
        print("lon1_test Failed")


def name_from_line_test():
    name1 = name_from_line("|name = Honolulu, Hawaii")
    name2 = name_from_line("|official_name = City and County of Honolulu")
    name3 = name_from_line("|conventional_long_name = Bolivarian Republic of Venezuela{{nobold|{{ref label|name|a|none}}}})")
    name4 = name_from_line("|native_name = {{unbulleted list|item_style=font-size:88%;")
    name5 = name_from_line("|native_name = BOBO{{unbulleted list|item_style=font-size:88%;")

    # test 1
    if name1 == "Honolulu, Hawaii":
        print("name_from_line Test1: Passed\n")
    else:
        print("name_from_line Test1: Failed")
        print(name1, "not", "Honolulu, Hawaii", "\n")
    # test 2
    if name2 == "City and County of Honolulu":
        print("name_from_line Test2: Passed\n")
    else:
        print("name_from_line Test2: Failed")
        print(name2, "not", "City and County of Honolulu", "\n")
    # test 3
    if name3 == "Bolivarian Republic of Venezuela":
        print("name_from_line Test3: Passed\n")
    else:
        print("name_from_line Test3: Failed")
        print(name3, "not", "Bolivarian Republic of Venezuela", "\n")
    # test 4
    if name4 is None:
        print("name_from_line Test4: Passed\n")
    else:
        print("name_from_line Test4: Failed")
        print(name4, "not", None, "\n")
    # test 5
    if name5 == "BOBO":
        print("name_from_line Test5: Passed\n")
    else:
        print("name_from_line Test5: Failed")
        print(name5, "not", "BOBO", "\n")


def test_is_valid_coord():

    if is_coord_str("n"):
        print("Passed")
    else:
        print("Error1")

    if is_coord_str("s"):
        print("Passed")
    else:
        print("Error2")
    if is_coord_str("e"):
        print("Passed")
    else:
        print("Error3")

    if is_coord_str("w"):
        print("Passed")
    else:
        print("Error4")

    if not is_coord_str("x"):
        print("Passed")
    else:
        print("Error5")

    if not is_coord_str("?"):
        print("Passed")
    else:
        print("Error6")

    if is_coord_str("180"):
        print("Passed")
    else:
        print("Error7")

    if is_coord_str("-180"):
        print("Passed")
    else:
        print("Error8")

    if is_coord_str("0"):
        print("Passed")
    else:
        print("Error9")

    if is_coord_str("90"):
        print("Passed")
    else:
        print("Error10")

    if is_coord_str("-90"):
        print("Passed")
    else:
        print("Error11")

    if not is_coord_str("1000"):
        print("Passed")
    else:
        print("Error12")

    if not is_coord_str("-181"):
        print("Passed")
    else:
        print("Error13")


def test_latlon_for_key():
    lats = "| latd = 51 | latm = 30 | lats = 26  | latNS = N".lower()
    lons = "| longd = 0 | longm = 7 | longs = 39 | longEW = W".lower()
    bad_line = "| latd =  | latm =      30 | lats = 26  | latNS = N".lower()
    peru = "|latd=12 |latm=2.6 |latNS=S |longd=77 |longm=1.7 |longEW=W"


    peru_latns = latlon_for_key("latns", peru)
    peru_lonew = latlon_for_key("longew", peru)



    latd1 = latlon_for_key("latd", lats)
    latm1 = latlon_for_key("latm", lats)
    lats1 = latlon_for_key("lats", lats)
    latns1 = latlon_for_key("latns", lats)

    lond1 = latlon_for_key("longd", lons)
    lonm1 = latlon_for_key("longm", lons)
    lons1 = latlon_for_key("longs", lons)
    lonew = latlon_for_key("longew", lons)

    latd2 = latlon_for_key("latd", bad_line)
    latm2 = latlon_for_key("latm", bad_line)




    if latns1 == "n":
        print("Test latns1 Passed")
    else:
        print("Test latns1 Failed: latns:", latns1, "not n")

    if lonew == "w":
        print("Test lonew Passed")
    else:
        print("Test lonew Failed")

    if (latd1 == 51):
        print("Test latd1 Passed")
    else:
        print("Test Failed: latd1:", latd1, "not 51")

    if (latm1 == 30):
        print("Test latm1 Passed")
    else:
        print("Test Failed: latm1:", latm1, "not 30")

    if (lats1 == 26):
        print("Test lats1 Passed")
    else:
        print("Test Failed: lats1", lats1, "not 26")

    if (lond1 == 0):
        print("Test lond1 Passed")
    else:
        print("Test Failed: lond1", lond1, "not 0")

    if (lonm1 == 7):
        print("Test lonm1 Passed")
    else:
        print("Test Failed: lonm1", lonm1, "not 7")

    if (lons1 == 39):
        print("Test lons1 Passed")
    else:
        print("Test Failed: lons1", lons1, "not 39")

    if (latd2 is None):
        print("Test latd2 Passed")
    else:
        print("Test Failed: latd2", latd2, "not", None)

    if (latm2 == 30):
        print("Test latm2 Passed")
    else:
        print("Test Failed: latm2", latm2, "not 30")


def test_coord_dict():
    line1 = "| coordinates {{Coord|0|40|S|90|33|W|scale:1400000|display=inline,title}}".lower()
    line2 = "|coor          ={{Coord|36|0|4|N|78|56|20|W|type:edu_region:US-NC|display=inline,title}}".lower()

    dict1 = coord_dict(line1)
    dict2 = coord_dict(line2)
    print("trying dict 2222j:")

    dict1_correct = {"latd": 0, "latm": 40, "latns": "S", "longd": 90, "longm": 33, "longew": "W"}
    dict2_correct = {"latd": 36, "latm": 0, "lats": 4, "latns": "N", "longd": 78, "longm": 56, "longs": 20, "longew": "W"}

    if set(dict1) == set(dict1_correct):
        print("Test1 Passed")
    else:
        print("Test1 Failed, dict1:", dict1, "not", dict1_correct)

    if set(dict2) == set(dict2_correct):
        print("Test2 Passed")
    else:
        print("Test2 Failed, dict2:", dict2, "not", dict2_correct)

pre_list = [
    (re.compile(r"(long|longitude|lons1)="), "lon="),
    (re.compile(r"(latitude|lats1)="), "lat="),
    (re.compile(r"(latitudedegrees|lat_deg|lat_d)="), "latd="),
    (re.compile(r"(latitudeminutes|lat_min|lat_m)="), "latm="),
    (re.compile(r"(latitudeseconds|lat_sec)="), "lats="),
    (re.compile(r"(lat_ns)="), "latns="),
    (re.compile(r"(longtitudedegrees|longitudedegrees|lon_deg|long_d)="), "longd="),
    (re.compile(r"(longtitudeminutes|longitudeminutes|lon_min|long_m)="), "longm="),
    (re.compile(r"(longtitudeseconds|longitudeseconds|lon_sec)="), "long="),
    (re.compile(r"(long_ew)="), "longew="),
]


def latlon_format_fix(page):
    #for process, subst in pre_list:
    #    page = process.sub(subst, page)
    page = re.sub(r"(long|longitude|lons1) *=", "lon=", page)
    page = re.sub(r"(latitude|lats1) *=", "lat=", page)

    page = re.sub(r'(latitudedegrees|lat_deg|lat_d) *=', "latd=", page)
    page = re.sub(r"(latitudeminutes|lat_min|lat_m) *=", "latm=", page)
    page = re.sub(r"(latitudeseconds|lat_sec) *=", "lats=", page)
    page = re.sub(r"(lat_ns) *=", "latns=", page)

    page = re.sub(r"(longtitudedegrees|longitudedegrees|lon_deg|long_d) *=", "longd=", page)
    page = re.sub(r"(longtitudeminutes|longitudeminutes|lon_min|long_m) *=", "longm=", page)
    page = re.sub(r"(longtitudeseconds|longitudeseconds|lon_sec) *=", "long=", page)
    page = re.sub(r"(long_ew) *=", "longew=", page)

    return page



# Import django transaction lib to turn off autocommit
# from django.db import transaction
# transaction.set_autocommit(False)

f = bz2.open(config.DATA_PATH)
error_boxes = None
num_error_boxes = 0
NON_LOC_UNUSABLE = 0
onDoc = 0
brackLevel = 0
onPage = False
onInfoBox = False
box = ""
num_boxes_processed = 0
bracketSum = 0
i = 0
num_locs = 0

for line in f:
    line = line.decode("utf-8")
    if '<page>' in line:
        onPage = True
        onInfoBox = False  # Is this nessiary
    elif '</page>' in line:
        onPage = False
    if onPage:
        if "{{Infobox" in line:
            bracketSum = 0
            onInfoBox = True

        if onInfoBox:
            bracketSum += line.count("{{") - line.count("}}")
            box += line
            # Exit the infobox
            if bracketSum == 0:
                # print(box, "\n\n\n\n\n")
                num_boxes_processed += 1
                if num_boxes_processed % 10000 == 0:
                    print("processed: ", num_boxes_processed)
                box = latlon_format_fix(box.lower())
                if is_location(box):
                    num_locs += 1
                    try:
                        add_loc(box)
                    except InvalidBox:
                        NON_LOC_UNUSABLE += 1
                    except:
                        if num_error_boxes % 10000 == 0:
                            if error_boxes is not None:
                                error_boxes.close()
                            error_boxes = open('error_boxes.txt', 'w')
                            print('opened error boxes')
                        error_boxes.write(box)
                        num_error_boxes += 1

                    if num_locs % 10000 == 0:
                        print(num_locs)
                        print("Scanned:", num_locs, " -- Total Errors:", NON_LOC_UNUSABLE)

                onInfoBox = False
                box = ''
                i += 1
            # Error Checking
            elif brackLevel < 0:
                raise Exception("Something went wrong in "
                                "finding the end of an infobox")


# close error
error_boxes.close()



# Clean Up Final Batch
# transaction.commit()
# Return to defualt autocommit state
# transaction.set_autocommit(True)

f.close()
"""
#name_from_line_test()
# decimal_degrees_from_dms_test()
#test_coord_vals()
#test_coord_dict()
#test_latlon_for_key()
#test_is_valid_coord()
test_add_loc()
"""
