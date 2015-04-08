import bz2

f = bz2.open("data\enwiki-20150304-pages-articles-multistream.xml.bz2")

onDoc = 0
brackLevel = 0
onPage = False
onInfoBox = False
box = ""
bracketSum = 0
i = 0
for line in f:
    line = line.decode("utf-8")
    # print(line)
    if '<page>' in line:
        onPage = True
    elif '</page>' in line:
        onPage = False
    if onPage:
        if "{{Infobox" in line:
            bracketSum = 0
            box = ""
            onInfoBox = True
            # Spin off to function extract_box_subject
            # + account for other cases
            boxSubject = line.strip("{{Infobox").strip(" ")
            # print(boxSubject)
            # Skip info box subject and move on to processing
            # The next line

        if onInfoBox:
            bracketSum += line.count("{{") - line.count("}}")
            box += line
            # Exit the infobox
            if bracketSum == 0:
                print(box.encode("utf-8"))
                onInfoBox = False
                i += 1
                if i == 100000:
                    break
            # Error Checking
            elif brackLevel < 0:
                raise Exception("Something went wrong in "
                                "finding the end of an infobox")

f.close()
