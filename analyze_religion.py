import csv
import json
from config import config

islam = ["islam", "muslim", "shi'a", "shia", "sunni", "alawite"]
christianity = ["christian", "catholic", "baptist", "calvini", "protestant",
                "episcopal", "lutheran", "congregationalist", "jehovah's witness",
                "unitarian", "presbyterian", "anglican"]
judaism = ["judaism", "jew", "hasidic", "haredi"]
budhism = ["buddhi"]
hinduism = ["hindu"]
mormonism = ["lds", "flds", "church of jesus christ of latter day saints"]
none = ["none", "atheism", "agnostic"]


def main():
    relig_freqs = religion_freqs(config.RELIGION_PATH)
    # print(relig_freqs)
    relig_sorted = sorted(relig_freqs.items(), key=lambda entry: entry[1], reverse=True)
    # THIS IS TESTING CODE
    #print_list(relig_sorted, 100)


    meta_cats = islam + christianity + judaism + budhism + hinduism + mormonism + none
    meta_freqs = meta_auth(meta_cats, relig_freqs)

    # Create the inverse dictonary before meta fields
    non_meta_inv_dict = inverse_dict(meta_freqs)
    #json.dump(non_meta_inv_dict, open('non_meta_inverse.json', 'w'))

    christian_dict = {}
    for key in christianity + mormonism:
        christian_dict[key] = meta_freqs[key]

    christian_dict = inverse_dict(christian_dict)

    #json.dump(christian_dict, open('christian_inverse.json', 'w'))

    # put categories together
    meta_freqs = merge_cats(meta_freqs, "judaism", judaism)
    meta_freqs = merge_cats(meta_freqs, "islam", islam)
    meta_freqs = merge_cats(meta_freqs, "christianity", christianity)
    meta_freqs = merge_cats(meta_freqs, "mormonism", mormonism)
    meta_freqs = merge_cats(meta_freqs, "no Religion", none)

    # Sort the meta dictionary
    x = sorted(meta_freqs.items(), key=lambda entry: entry[1]['meta_freq'],
               reverse=True)

    # print_meta_auth(meta_freqs)
    total_freq = 0
    for freq in relig_freqs.values():
        total_freq += freq

    # calculate freq of meta category
    unused = missed_religions(meta_freqs, relig_freqs)
    missed_freq = 0
    for relig in unused:
        missed_freq += relig_freqs[relig]


    # big one mapping fields to meta catagories
    meta_inv_dict = inverse_dict(meta_freqs)
    #json.dump(meta_inv_dict, open('big_inverse.json', 'w'))


    print_meta_auth(meta_freqs)

    # how many instances of religions we missed
    print("total freq: ", total_freq, "missed: ", missed_freq,
          "freq captured: ", total_freq - missed_freq)


def inverse_dict(a_dict):
    inv_dict = {}
    for meta_category in a_dict.keys():
        print(a_dict[meta_category])
        for subcategory in a_dict[meta_category]['subcats']:
            inv_dict[subcategory] = meta_category
    return inv_dict


def missed_religions(meta_auth, all_religions):
    """
    returns a list of religions that are not present in the given
    meta authority list
    """

    meta_subcats = []
    missed_relig = []

    for super_cat in meta_auth.keys():
        meta_subcats.extend(meta_auth[super_cat]['subcats'])

    missed_relig = [x for x in all_religions if x not in meta_subcats]
    return missed_relig


def merge_cats(meta_auth, super_cat_name, cats_to_merge):
    # TODO frequency does not work
    super_cat = meta_auth[cats_to_merge[0]]
    for cat in cats_to_merge[1:]:  # go through each category
        subcats = meta_auth[cat]['subcats']
        for subcat in subcats:
            if subcat not in super_cat['subcats']:
                super_cat['subcats'].append(subcat)

    # remove all combined cats from meta_auth
    for cat in cats_to_merge:
        meta_auth.pop(cat)
    # add super cat
    meta_auth[super_cat_name] = super_cat
    return meta_auth


def print_meta_auth(meta_auth):
    for key, value in meta_auth.items():
        print("Meta_Cat:", key, "  Freq:", value['meta_freq'], "\n")
        for subcat in value['subcats']:
            print("\t", subcat)
        print("\n\n\n")


def meta_auth(cats, religs):
    """
    given a list of meta categories (i.e. keywords) creates a new authority 
    list with frequencies of meta categories and subcategories contained in 
    those mc
    """
    meta_auth = {}

    for subcat, freq in religs.items():
        meta_for_sub = 0
        for meta_cat in cats:
            # check if meta cat appears in sub cat
            if meta_cat in subcat:  # this may cause encoding issue
                meta_for_sub += 1
                # check if entries under meta category exist
                if meta_cat in meta_auth:
                    # add to subcats
                    meta_auth[meta_cat]['subcats'].append(subcat)
                    meta_auth[meta_cat]['meta_freq'] += freq
                else:
                    meta_auth[meta_cat] = {'subcats': [subcat], 'meta_freq': freq}

            # if meta_for_sub > 2:
            #     print("subcat: ", subcat, "with frequency: ", freq, "is in: ",
            #           meta_for_sub, "meta categories")
    return meta_auth


def print_list(a_list, max_print):
    i = 0
    for item in a_list:
        if i == max_print:
            return
        print(item)
        i += 1


def religion_freqs(file_path):
    religion_freqs = {}
    with open(file_path) as f:
        reader = csv.reader(f)
        for row in reader:
            row = json.loads(row[0])
            # create frequency list for religions
            for religion in row:  # list of religions in row
                religion = religion.strip().lower()
                if religion in religion_freqs:
                    religion_freqs[religion] += 1
                else:
                    religion_freqs[religion] = 1
    return religion_freqs
            # print([x.encode("utf-8").lower().strip() for x in row])
            # simplejson.loads(row, "utf-8")

main()

# x = filter(lambda entry: entry[1] > 1, x)

# Forbes
