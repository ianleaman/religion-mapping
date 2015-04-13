import re
import sys


def is_person(box):
    is_person = False
    if "birth_place" in box or "death_place" in box and "religion" in box:
        is_person = True
    return is_person


def processBox(box):
    #  split newline
    box_json = None
    box = box.lower()  # dont want case to mess with processing
    if is_location(box):
        box_json = json_from_loc_box(box)
    elif is_person(box):
        box_json = json_from_person_box(box)


def is_location(box):
    is_location = False
    if "latd" in box and "longd" in box:
        is_location = True
    elif "coord" in box:
        is_location = True
    return is_location


    #  pair w/ equals
    #  remove refs (anything w tag)
    #  clean out links
def json_from_loc_box(box):
    box_fields = box.split("\n")
    field_dict = {}
    for line in box_fields:  #  the order of the ifs matters
        if "en_name" in line:
            field_dict["en_name"] = name_from_line(line)

        elif "conventional_long_name" in line:
            field_dict["conventional_long_name"] = name_from_line(line)

        elif "official_name" in line:
            field_dict["official_name"] = name_from_line(line)

        elif "native_name" in line:
            field_dict["native_name"] = name_from_line(line)

        elif "other_name" in line:
            field_dict["other_name"] = name_from_line(line)

        elif "name" in line:
            field_dict["name"] = name_from_line(line)

        elif "coord" in line:
            #  need to figure out how to extract
            field_dict["lat"] = latitude_from_coord(line)
            field_dict["lon"] = longitude_from_coord(line)

        elif "latd" in line:
            field_dict["lat"] = decimal_degrees_from_dms(line)

        elif "lond" in line:
            field_dict["lon"] = decimal_degrees_from_dms(line)


def name_from_line(line):
    name = None
    key_value = line.split("=", 1)
    if len(key_value) == 2:  # check that the line had both key and value
        dirty_name = key_value[1]
        name = re.split("&|\||{|{{", dirty_name, 1)[0]  # exclude nonsense
        name = name.strip()
    else:
        print("ERRROR_bad_name_line")
    if name == "":
        name = None
    return name


def longitude_from_coord():
    """
    | coordinates= {{Coord|0|40|S|90|33|W|scale:1400000|display=inline,title}}
    """


def latitude_from_coord():
    """
    | coordinates= {{Coord|0|40|S|90|33|W|scale:1400000|display=inline,title}}
    """


def decimal_degrees_from_dms(dms_string):
    dms_array = dms_string.split("|")
    print(dms_array)
    decimal_degrees = None
    degrees = None
    minutes = None
    seconds = None
    is_north = 3  # arbitrary val not TRUE OR FALSE TODO: THIS DOES NOT WORK
    if len(dms_array) == 5:
        degree_key_val = dms_array[1].split("=")
        print("degree_kv", degree_key_val)
        minute_key_val = dms_array[2].split("=")
        second_key_val = dms_array[3].split("=")
        north_south_key_val = dms_array[4].split("=")
        if len(degree_key_val) == 2:
            degrees = int(degree_key_val[1].strip())
            print("degrees", degrees)
        if len(minute_key_val) == 2:
            minutes = int(minute_key_val[1].strip())
        if len(second_key_val) == 2:
            seconds = int(second_key_val[1].strip())
        if len(north_south_key_val) == 2:
            is_north = north_south_key_val[1].strip() == "N"

    if degrees is not None and minutes is not None and seconds is not None:
        decimal_degrees = degrees + minutes/60.0 + seconds/3600.0
        print(is_north)
    return decimal_degrees


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

name_from_line_test()
decimal_degrees_from_dms_test()
