import requests

from .utils import date_or_none


def get_transit_data(stop: str):
    api_url = (f'http://transport.opendata.ch/v1/stationboard?'
               f'station={stop}&limit=10')
    response = requests.get(api_url)
    response.raise_for_status()

    return response.json()


def get_departures(transit_data):
    departures = transit_data['stationboard']

    for departure in departures:
        scheduled = date_or_none(departure['stop']['departure'])
        exp = date_or_none(departure['stop']['prognosis']['departure'])
        name = departure['number']
        to = departure['to']

        if name.startswith('T '):
            name = name[2:]

        yield name, scheduled, exp, to


def departures_per_destination(stop):
    departures = get_departures(stop)
    destinations = {}
    for name, scheduled, exp, to in departures:
        destinations.setdefault(to, []).append((name, scheduled, exp))

    return destinations
