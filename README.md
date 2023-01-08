# About

A Python script to request results from the entscheidsuche.ch elastic API and serve them as an RSS feed. 

# How it works

1. The file `checked_ids.csv` is checked for case ids
2. A query is made to the entscheidsuche.ch elastic API
3. IDs in the `checked_ids.csv` and duplicates are removed from the results, remaining hits are stored in `new_hits.json`
4. Feedgen generates an RSS feed with remaining hits
5. New hits given to the feed have their IDs stored in the `checked_ids.csv` for the next run

# Get Started

1. Set up:
```
git clone https://github.com/quadratecode/entscheidsuche-rss-generator
pip3 install -r requirements.txt
```
2. Adjust the requested date in `generate_feed.py` range to your liking. Please note that the entscheidsuche.ch API limits the number of returned results to 10. Depending on how broad your query is, the time intervall should be set accordingly. Be mindful of the load you create on the entscheidsuche.ch servers.

3. Adjust the example query in `generate_feed.py` to your liking. Please see the [entscheidsuche.ch](https://entscheidsuche.ch/pdf/EntscheidsucheAPI.pdf) (PDF) API and the [elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html) docs for further details.

Here is an empty example record:

```json
{
    "_index": "",
    "_type": "",
    "_id": "",
    "_score": 0.0,
    "_source": {
        "date": "",
        "hierarchy": [
            "",
            "",
            ""
        ],
        "abstract": {
            "de": "",
            "it": "",
            "fr": ""
        },
        "source": "",
        "title": {
            "de": "",
            "it": "",
            "fr": ""
        },
        "reference": [
            "",
            ""
        ],
        "attachment": {
            "content_type": "",
            "language": "",
            "content_url": "",
            "source": "",
            "content": "",
            "content_length": 0
        },
        "meta": {
            "de": "",
            "it": "",
            "fr": ""
        },
        "canton": "",
        "id": ""
    }
}
```
For example, if you would like to be alerted about BGEs within the desired date range you could set a query like so:

```python
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
                    "wildcard": {
                        "id": {
                            "value": "*BGE*",
                        }
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
```

Or just remove the "wildcard" clause from the query if you want to fetch all results (will exceed API limit per call):

```python
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
```

4. Set name, address and description of your feed, adjust extracted fields as needed.

5. Set up as a cron job on your server to run the script periodically according to your query parameters.

6. Subscribe to the feed through the reader of your choice.

# Copyright and License

Source of results: [https://entscheidsuche.ch/](https://entscheidsuche.ch/)

The original content of this repository is licensed under [MIT](https://github.com/quadratecode/entscheidsuche-rss-generator/blob/main/LICENSE).
