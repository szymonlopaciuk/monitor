import re

from PIL import Image, ImageDraw, ImageFont
from typing import Literal

from .style import ColorScheme, Font


def draw_time_with_delay(
        im: ImageDraw,
        time: str,
        extra: str,
        position: tuple[int, int],
):
    if not re.compile(r'\d\d:\d\d').match(time):
        raise ValueError(f'Invalid time format: {time}')

    x, y = position
    time_w = 55
    im.text((x, y), time, font=Font.BODY, fill=ColorScheme.BLACK)
    im.text((x + time_w, y), extra, font=Font.BODY, fill=ColorScheme.ACCENT)


def draw_text(
        im: ImageDraw,
        position: tuple[int, int],
        text: str,
        font: ImageFont = Font.BODY,
        fill: ColorScheme = ColorScheme.BLACK,
        valign: Literal['top', 'middle', 'bottom'] = 'middle',
        halign: Literal['left', 'center', 'right'] = 'center',
):
    x, y = position
    w, h = font.getsize(text)

    delta_x, delta_y = 0, 0

    match valign:
        case 'middle':
            delta_y = -h / 2
        case 'bottom':
            delta_y = -h

    match halign:
        case 'center':
            delta_x = -w / 2
        case 'right':
            delta_x = -w

    im.text((x + delta_x, y + delta_y), text, font=font, fill=fill)
    return x + delta_x + w, y + delta_y + h


def draw_image(
        im: ImageDraw,
        position: tuple[int, int],
        image: Image,
        fill: ColorScheme = ColorScheme.BLACK,
        valign: Literal['top', 'middle', 'bottom'] = 'middle',
        halign: Literal['left', 'center', 'right'] = 'center',
):
    x, y = position
    w, h = image.size

    delta_x, delta_y = 0, 0

    match valign:
        case 'middle':
            delta_y = -h / 2
        case 'bottom':
            delta_y = -h

    match halign:
        case 'center':
            delta_x = -w / 2
        case 'right':
            delta_x = -w

    im.bitmap((x + delta_x, y + delta_y), image, fill=fill)
    return x + delta_x + w, y + delta_y + h
