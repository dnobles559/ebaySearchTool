#!/usr/bin/env python
# coding: utf-8

from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import pandas as pd
import os

ITEMS_PER_PAGE = 100 # max = 100

# Ebay search
def searchEbay(searchTerms, page_num=1):

    ebay_pricelist = pd.DataFrame()
    try:
        api = Finding(config_file='ebay.yaml', debug=False, siteid="EBAY-US")

        request = {
            'keywords': searchTerms,
            'itemFilter': {
                'name': 'condition',
                'value': 'used'
            },
            'paginationInput': {
                'entriesPerPage': ITEMS_PER_PAGE, # max = 100
                'pageNumber': page_num
            },
        }

        response = api.execute('findItemsByKeywords', request)

        if int(response.dict()['searchResult']["_count"]) != 0:
            for item in response.dict()['searchResult']['item']:
                price = item['sellingStatus']['convertedCurrentPrice']['value']
                name = item['title']
                info_to_keep = {
                    'price': price,
                    'name': name
                }

                ebay_pricelist = ebay_pricelist.append(info_to_keep, ignore_index=True)
                ebay_pricelist['price'] = ebay_pricelist['price'].astype(float)

    except ConnectionError as e:
        print(e)
        print(e.response.dict())



    return ebay_pricelist

import pandas as pd
from craigslist import CraigslistForSale

def searchCL(searchTerms):
    print "searching craigslist..."

    locations = [
                    ('sandiego', 'nsd'),
                    ('sandiego', 'csd'),
                    ('sandiego', 'ssd'),
                    ('sandiego', 'esd')
                ]

    cl_pricelist = pd.DataFrame()
    for site, area in locations:
        # CraigslistForSale.show_filters()
        cl_h = CraigslistForSale(site='sandiego', area='csd', category='pha',
                                 filters={
                                             'query': searchTerms,
                                             'bundle_duplicates': 'True'
                                         })

        response = cl_h.get_results(sort_by='newest', geotagged=True)

        for item in response:
            cl_pricelist = cl_pricelist.append(item, ignore_index=True)


    # data clean-up
    cl_pricelist['price'] = cl_pricelist['price'].astype(str).str.replace('$', '').astype(float)
    # check that there aren't duplicates, by comparing description, price, etc
    return cl_pricelist

def analysis(input_df, source=""):
    if len(input_df) == 0:
        return "no data\n\n"

    else:

        output = "-- ANALYSIS OF " + source + " RESULTS --"
        output = output + "\n" + "num of samples: " + str(len(ebay_pricelist))
        output = output + "\n" + "mean: $%0.2f" % input_df.mean()['price']
        output = output + "\n" + "std:  $%0.2f\n\n" % input_df.std()['price']

        return  output

def cleanup(input_df):
    # e is remove, to mimick gmail
    # x is exit
    for idx, item in input_df.iterrows():
        print item['name']
        user_input = raw_input("")
        if user_input == 'e':
            input_df = input_df.drop(idx)
        elif user_input == 'x':
            break

searchTerms = 'canon t3'
num_pages = 2
ebay_pricelist = searchEbay(searchTerms)

# Get prices from Ebay
for i in range(1, num_pages):
    new_results = searchEbay(searchTerms, i)
    ebay_pricelist = ebay_pricelist.append(new_results)

    # if the search doesn't have enough results to fill the page..
    if len(new_results) < ITEMS_PER_PAGE:
        break
    print i, "\r",

print analysis(ebay_pricelist, source="EBAY")
os.system('say "done"')

searchTerms = 'DSLR'
cl_pricelist = searchCL(searchTerms)

print " -- e = delete item from list    --"
print " -- x = exit program             --"
print " -- nothing = skip item          --"
print " -- [string] = ebay search terms --"
print " -- ---------------------------- --\n\n"

for idx, item in cl_pricelist.iterrows():
    print item['name'] + ", $%0.2f" % item['price']

    user_input = raw_input("enter search terms: ")

    if user_input == '':
        continue
    elif user_input == 'x':
        print "\n...\nexiting\n...\n"
        break

    print "ebay analysis: " + analysis(searchEbay(user_input))


# In[ ]:


# TODO: Autosort for potential profit
# create list of camera names I know
# search ebay for the cameras I know
standard_cameras = [
                    'canon 5d mark iii',
                    'canon 5d mark iv',
                    'canon 6d mark i'
                    'canon 6d mark ii',
                    'sony a7r'
                   ]

# create "compare to" columns in the cl dataframe
# match the cameras I know to the compare to columns

# organize by potential profit

# TODO: Generate a list of items to remove from the main list
# eg "AS-IS"
bad_keywords = ['as-is', 'broken', 'not working', 'lens']
# OR, we could try to buy kits, and part them out as individual components... (ie don't treat lens as a bad word)
