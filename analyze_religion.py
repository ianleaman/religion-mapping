import csv
import json
from config import config

religion_freqs = {}
with open(config.RELIGION_PATH) as f:
    reader = csv.reader(f)
    for row in reader:
        row = json.loads(row[0])
        for religion in row:
            religion = religion.strip().lower()
            if religion in religion_freqs:
                religion_freqs[religion] += 1
            else:
                religion_freqs[religion] = 1
        # print([x.encode("utf-8").lower().strip() for x in row])
        # simplejson.loads(row, "utf-8")

# Sort the dictionary
x = sorted(religion_freqs.items(), key=lambda entry: -entry[1])
# x = filter(lambda entry: entry[1] > 1, x)
x = [entry for entry in x if entry[1] > 5]
print(len(x))
for i, item in enumerate(x):
    print(item[0].encode("utf-8"), item[1])
    if i == 1000:
        break


# Forbes
