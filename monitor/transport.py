import requests

from .utils import date_or_none


def get_departures():
    API_URL = ('http://transport.opendata.ch/v1/stationboard?'
               'station=Saint-Genis,%20Champ-Fusy&limit=10')
    response = requests.get(API_URL)
    response.raise_for_status()

    departures = response.json()['stationboard']
    for departure in departures:
        scheduled = date_or_none(departure['stop']['departure'])
        exp = date_or_none(departure['stop']['prognosis']['departure'])
        name = departure['number']
        to = departure['to']

        if name.startswith('T '):
            name = name[2:]

        yield name, scheduled, exp, to


def departures_per_destination():
    departures = get_departures()
    destinations = {}
    for name, scheduled, exp, to in departures:
        destinations.setdefault(to, []).append((name, scheduled, exp))

    return destinations
