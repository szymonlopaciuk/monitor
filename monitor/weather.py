import requests
import monitor.res.svg
import monitor.res.bitmap

from cairosvg import svg2png
from importlib_resources import files
from PIL import Image
from typing import Literal


ICON_MAP = {
    '0': ('wi-day-sunny', 'wi-night-clear'),
    '1': ('wi-day-sunny-overcast', 'wi-night-alt-partly-cloudy'),
    '2': ('wi-day-cloudy', 'wi-night-alt-cloudy'),
    '3': 'wi-day-cloudy',
    '45': ('wi-day-fog', 'wi-night-fog'),
    '48': ('wi-day-fog', 'wi-night-fog'),
    '51': ('wi-day-sprinkle', 'wi-night-alt-sprinkle'),
    '53': 'wi-sprinkle',
    '55': 'wi-sprinkle',
    '56': ('wi-day-sleet', 'wi-night-alt-sleet'),
    '57': 'wi-sleet',
    '61': ('wi-day-rain', 'wi-night-alt-rain'),
    '63': 'wi-rain',
    '65': 'wi-rain',
    '66': ('wi-day-sleet', 'wi-night-alt-sleet'),
    '67': 'wi-sleet',
    '71': ('wi-day-snow', 'wi-night-alt-snow'),
    '73': 'wi-snow',
    '75': 'wi-snow',
    '77': 'wi-snowflake-cold',
    '80': ('wi-day-showers', 'wi-night-alt-showers'),
    '81': 'wi-showers',
    '82': 'wi-showers',
    '85': ('wi-day-snow', 'wi-night-alt-snow'),
    '86': 'wi-snow',
    '95': ('wi-day-thunderstorm', 'wi-night-alt-thunderstorm'),
    '96': ('wi-day-hail', 'wi-night-alt-hail'),
    '99': 'wi-hail',
}


DESCRIPTION_MAP = {
    '0': 'Clear sky',
    '1': 'Mainly clear',
    '2': 'Partly cloudy',
    '3': 'Overcast',
    '45': 'Fog',
    '48': 'Rime fog',
    '51': 'Light drizzle',
    '53': 'Moderate drizzle',
    '55': 'Dense drizzle',
    '56': 'Light freezing drizzle',
    '57': 'Dense freezing drizzle',
    '61': 'Slight rain',
    '63': 'Moderate rain',
    '65': 'Heavy rain',
    '66': 'Light freezing rain',
    '67': 'Heavy freezing rain',
    '71': 'Slight snow fall',
    '73': 'Moderate snow fall',
    '75': 'Heavy snow fall',
    '77': 'Snow grains',
    '80': 'Slight rain showers',
    '81': 'Moderate rain showers',
    '82': 'Violent rain showers',
    '85': 'Slight snow showers',
    '86': 'Heavy snow showers',
    '95': 'Thunderstorm',
    '96': 'Thunderstorm with hail',
    '99': 'Thunderstorm with heavy hail',
}


def get_icon_for_weathercode(code: int, time: Literal['day', 'night']) -> Image:
    """
    0	        Clear sky
    1, 2, 3	    Mainly clear, partly cloudy, and overcast
    45, 48	    Fog and depositing rime fog
    51, 53, 55	Drizzle: Light, moderate, and dense intensity
    56, 57	    Freezing Drizzle: Light and dense intensity
    61, 63, 65  Rain: Slight, moderate and heavy intensity
    66, 67      Freezing Rain: Light and heavy intensity
    71, 73, 75  Snow fall: Slight, moderate, and heavy intensity
    77          Snow grains
    80, 81, 82  Rain showers: Slight, moderate, and violent
    85, 86      Snow showers slight and heavy
    95          Thunderstorm: Slight or moderate
    96, 99      Thunderstorm with slight and heavy hail
    """
    icon_name = ICON_MAP.get(str(code))
    match icon_name, time:
        case (day, _), 'day':
            icon_name = day
        case (_, night), 'night':
            icon_name = night

    pngs = files(monitor.res.bitmap)
    svgs = files(monitor.res.svg)
    png_file = pngs / f'{icon_name}.png'
    svg_file = svgs / f'{icon_name}.svg'

    if png_file.is_file():
        return Image.open(str(png_file))

    svg2png(
        url=str(svg_file),
        output_width=64,
        output_height=64,
        write_to=str(png_file),
    )
    return Image.open(str(png_file))


def get_description_for_weathercode(code: int) -> str:
    return DESCRIPTION_MAP.get(str(code), 'Unknown')


def get_weather_raw():
    API_URL = ('https://api.open-meteo.com/v1/forecast?'
               'latitude=46.20&'
               'longitude=6.15&'
               'hourly=temperature_2m,relativehumidity_2m,rain&'
               'daily=weathercode,temperature_2m_max,temperature_2m_min&'
               'current_weather=true&'
               'timezone=auto')
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()
