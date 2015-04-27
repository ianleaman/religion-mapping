import csv
import json
from config import config


# people_type = "_all.csv"
# authority_list = json.load(open("data/big_inverse.json"))

people_type = "_all_meta.csv"
authority_list = json.load(open("data/non_meta_inverse.json"))

# people_type = "_christian_mormon.csv"
# authority_list = json.load(open("data/christian_inverse.json"))


class people:
    LON = 0
    LAT = 1
    BIRTH_YEAR = 2
    DEATH_YEAR = 3
    RELIGION = 4
    PARTY = 5
    SUBJECT = 6


header = ["lon", "lat", "year", "religion", "subject"]


new_f = open(config.FINAL_PEOPLE_PATH + people_type, 'w',
             encoding='utf-8', newline="")


with open(config.PEOPLE_PATH) as f:
    writer = csv.writer(new_f, delimiter='\t',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

    reader = csv.reader(f, delimiter="\t")

    writer.writerow(header)
    # Skipp people header
    next(reader)
    errors = 0
    nonErrors = 0
    for row in reader:
        lon = row[people.LON]
        lat = row[people.LAT]
        birth_year = row[people.BIRTH_YEAR]
        death_year = row[people.DEATH_YEAR]
        religion_list = json.loads(row[people.RELIGION])
        subject = row[people.SUBJECT]

        numLoops = 5
        if birth_year and death_year:
            numLoops = int(death_year) - int(birth_year)
            if numLoops < 1:
                numLoops = 1

        year = birth_year if (birth_year and not birth_year == "null") else death_year

        processed_religions = set()
        for religion in religion_list:
            religion = religion.lower().strip()
            if religion in authority_list:
                processed_religions.add(authority_list[religion])
                nonErrors += 1
            else:
                errors += 1
                # print(religion)

        for i in range(0, numLoops):
            for religion in processed_religions:
                new_row = [lon, lat, int(year) + i, religion, subject]
                writer.writerow(new_row)

    print(nonErrors, errors)

'''
What we want:
    - Fields to groupings
    - All fields mapping to their containing words
        - for everything
        - then for islam, christianity and jewdiasm
'''
