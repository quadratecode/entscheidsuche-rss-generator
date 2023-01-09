import requests
import json
import csv
import arrow
from feedgen.feed import FeedGenerator
import sys
import logging

# §§
# LICENSE: https://github.com/quadratecode/entscheidsuche-rss-generator/blob/main/LICENSE
# §§

# Result source: https://entscheidsuche.ch/
# API docs for entscheidsuche.ch: https://entscheidsuche.ch/pdf/EntscheidsucheAPI.pdf

# Create logfile
logging.basicConfig(filename="logfile.log", level=logging.INFO)

# create an empty set
ids = set()

# load IDs of already checked cases stored in checked_ids.csv
with open("checked_ids.csv", 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        ids.add(row[0])

# get the current date and time
now = arrow.now()

# calculate the start date from today
# API limits results quantity, so dont overextend the timeframe
start_date = now.shift(days=-3)

# format the start and end dates as strings
start_date_str = start_date.format("YYYY-MM-DD")  # your start date here
end_date_str = now.format("YYYY-MM-DD")  # your end date here

# set query (see elastic search docs for details)
# this example query checks for two keywords
query = {
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "date": {
                            "gte": start_date_str,
                            "lte": end_date_str
                        }
                    }
                },
                {
                    "multi_match": {
                        "query": "*keyword1* *keyword2*",
                        "fields": ["attachment.content"]
                    }
                }
            ],
            "must_not": {
                "terms": {
                    "_id": list(ids)
                }
            }
        }
    }
}

# send the search request
logging.info(str(now) + ": Request sent")
response = requests.get("https://entscheidsuche.ch/_search.php", json=query)

# get the search results
results = response.json()

# try to get the list of hits from the search results
number_of_hits = results["hits"]["total"]["value"]
# exit script if no hits are found
if number_of_hits == 0:
    logging.info(str(now) + ": No hits found")
    sys.exit()
else:
    hits = results["hits"]["hits"]

# create an empty list to store new hits
new_hits = []

# loop through the hits
for hit in hits:
    # get the ID of the hit
    hit_id = hit["_id"]

    # check if the ID is already in the set
    if hit_id in ids:
        # if it is, skip it
        continue

    # if it's not, add it to the set
    ids.add(hit_id)
    new_hits.append(hit)

# check if there are any new hits
if len(new_hits) == 0:
    logging.info(str(now) + ": No new hits found")
    sys.exit()
else:
    logging.info(logging.info(str(now) + ": " + str(len(new_hits)) + " hits found"))

# create a dictionary to store the hits, using the IDs as keys
hits_dict = {hit_id: hit for hit_id, hit in zip(ids, hits)}

# write the dictionary of hits to the file
with open('new_hits.json', 'w') as f:
    json.dump(new_hits, f, indent=2)

# create a new feed
feed = FeedGenerator()

# set the title, link, and description of the feed
feed.title("Case Feed")
feed.link(href="http://example.com/feed.rss", rel="alternate")
feed.description("A feed of newly published court cases")

for hit in new_hits:
    # add the entry to the feed
    entry = feed.add_entry()

    # set the title, link, and description of the entry
    try:
        entry.title(hit["_source"]["title"]["de"]) # in German
    except KeyError:
        logging.info(logging.info(str(now) + ": Skip entry title, not found"))
        pass
    try:
        entry.link(href=hit["_source"]["attachment"]["content_url"])
    except KeyError:
        logging.info(logging.info(str(now) + ": Skip entry URL, not found"))
        pass
    try:
        entry.description(hit["_source"]["abstract"]["de"]) # in German
    except KeyError:
        logging.info(logging.info(str(now) + ": Skip entry description, not found"))
        pass

# generate the RSS feed, save to file
feed.rss_file("case_feed_rss.xml")

# write the updated set of IDs to the CSV file for next run
with open("checked_ids.csv", "w") as f:
    writer = csv.writer(f)
    for id in ids:
        writer.writerow([id])
