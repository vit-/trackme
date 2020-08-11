import typing as t

from dataclasses import dataclass
from datetime import datetime, timedelta

from dateutil.parser import parse as parse_date
from elasticsearch import Elasticsearch


@dataclass(frozen=True)
class Location:
    date: datetime
    lat: float
    lon: float


@dataclass(frozen=True)
class Trip:
    start_date: datetime
    stop_date: datetime


INDEX = 'telemetry-*'


def get_last_location(es: Elasticsearch, start_date: datetime = None, gps_fix: bool = True) -> t.Optional[Location]:
    if start_date is None:
        start_date = datetime.utcnow() - timedelta(hours=1)

    query = {
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            '@timestamp': {
                                'gte': start_date,
                            },
                        },
                    },
                ]
            }
        }
    }
    if gps_fix:
        query['query']['bool']['must'].append({
            'term': {
                'fix_status': {
                    'value': 1,
                },
            },
        })
    result = es.search(index=INDEX, body=query, size=1, sort='@timestamp:desc')
    if result['hits']['total'] == 0:
        return
    hit = result['hits']['hits'][0]['_source']

    return Location(
        date=parse_date(hit['@timestamp'], ignoretz=True),
        lat=hit['geo']['lat'],
        lon=hit['geo']['lon'],
    )


def get_trips(es: Elasticsearch, start_date: datetime = None, stop_date: datetime = None) -> t.List[Trip]:
    if stop_date is None:
        stop_date = datetime.utcnow()
    if start_date is None:
        start_date = stop_date - timedelta(days=7)

    submit_interval_secs = 10
    min_speed = 5
    resolution_secs = 5 * 60
    resolution_millis = resolution_secs * 1000
    min_doc_count = 0.75 * resolution_secs / submit_interval_secs

    min_trips_split_delay = timedelta(minutes=15)

    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_date,
                                "lt": stop_date,
                            }
                        }
                    },
                    {
                        "range": {
                            "speed": {
                                "lte": min_speed,
                            }
                        }
                    },
                    {
                        'term': {
                            'fix_status': {
                                'value': 1,
                            },
                        },
                    },
                ]
            }
        },
        "aggs": {
            "time": {
                "date_histogram": {
                    "field": "@timestamp",
                    "fixed_interval": "{}s".format(resolution_secs),
                    "min_doc_count": min_doc_count,
                }
            }
        }
    }
    result = es.search(index=INDEX, body=query, size=0)
    buckets = result['aggregations']['time']['buckets']
    start = start_date.timestamp() * 1000
    trips = []
    for bucket in buckets:
        maybe_end = bucket['key']
        if maybe_end - start > resolution_millis:
            trips.append(Trip(
                start_date=datetime.fromtimestamp(start/1000),
                stop_date=datetime.fromtimestamp(maybe_end/1000),
            ))
        start = maybe_end

    merged_trips = []
    cur_trip = trips[0]
    for trip in trips[1:]:
        if trip.start_date - cur_trip.stop_date <= min_trips_split_delay:
            cur_trip = Trip(start_date=cur_trip.start_date, stop_date=trip.stop_date)
        else:
            merged_trips.append(cur_trip)
            cur_trip = trip
    merged_trips.append(cur_trip)
    return merged_trips
