import click
import requests

from datetime import datetime
from typing import Optional
from dateutil.parser import parse as parse_date
from PIL import Image, ImageDraw, ImageFont


class ColorScheme:
    BLACK = 0
    ACCENT = 1
    WHITE = 2
    BLACK_RGB = (0, 0, 0)
    ACCENT_RGB = (255, 0, 0)
    WHITE_RGB = (255, 255, 255)

    @classmethod
    def make_palette(cls):
        color_map = {
            cls.BLACK: cls.BLACK_RGB,
            cls.ACCENT: cls.ACCENT_RGB,
            cls.WHITE: cls.WHITE_RGB,
        }

        palette = [0, 0, 0] * 255
        for color_id, rgb in color_map.items():
            palette[color_id * 3:color_id * 3 + 3] = rgb

        return palette


class Font:
    H1 = ImageFont.truetype('Inter-Bold', 24)
    BODY = ImageFont.truetype('Inter-Medium', 26)

def date_or_none(datetime_string: Optional[str]) -> Optional[datetime]:
    if not datetime_string:
        return None

    return parse_date(datetime_string)


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


@click.command()
@click.option(
    '-o', '--output', type=click.Choice(['pil', 'spi']),
    default='pil',
    help='How to display the image',
)
def run(output):
    print('Running monitor')

    im = Image.new('P', (800, 480), ColorScheme.WHITE)
    im.putpalette(ColorScheme.make_palette())
    draw = ImageDraw.Draw(im)

    draw.text((10, 10), 'Champ-Fusy Departures', font=Font.H1, fill=ColorScheme.BLACK)
    for i, (name, scheduled, exp, to) in enumerate(get_departures()):
        y = 50 + i * 40

        box_w = 50
        w, h = Font.BODY.getsize(name)
        draw.rounded_rectangle((10, y, 10 + box_w, y + 32), 16, fill=ColorScheme.BLACK)
        draw.text((10 + (box_w - w)/2, y), name, font=Font.BODY, fill=ColorScheme.WHITE)

        draw.text((80, y), to, font=Font.BODY, fill=ColorScheme.BLACK)

        draw.text((500, y), f'{scheduled:%H:%M}', font=Font.BODY, fill=ColorScheme.BLACK)

        if exp:
            #delay = int((exp - scheduled).total_seconds() / 60)
            #draw.text((600, y), f'{delay:+}\'', font=Font.BODY, fill=Color.ACCENT)
            draw.text((600, y), f'exp. {exp:%H:%M}', font=Font.BODY, fill=ColorScheme.ACCENT)

    if output == 'pil':
        im.show()
