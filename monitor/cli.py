import click

from logging import getLogger
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw

from .display import display_clear, display_show
from .draw import draw_time_with_delay, draw_text, draw_image
from .style import ColorScheme, Font
from .transport import get_transit_data, get_departures
from .utils import angle_to_compass, date_or_none
from .weather import (
    get_description_for_weathercode,
    get_icon_for_weathercode,
    get_weather_raw,
)


logger = getLogger(__name__)


@click.group()
def entrypoint():
    """Monitor CLI interface."""
    pass


@entrypoint.command('run')
@click.option(
    '-o', '--output', type=click.Choice(['pil', 'epd']),
    default='pil',
    help='How to display the image',
)
@click.option(
    '-f', '--flip', default=False, is_flag=True,
    help='If set, the image will be rotated by 180°',
)
@click.option(
    '-t', '--transit-stop', required=True,
    help='Name of the public transport stop or station to monitor',
)
def run(output, flip, transit_stop):
    logger.info('Running monitor')

    im = Image.new('P', (480, 800), ColorScheme.WHITE)
    im.putpalette(ColorScheme.make_palette())
    draw = ImageDraw.Draw(im)

    # Constants
    section_gap = 40

    # Transportation info
    _, y = draw_text(draw, (10, 10), f'Public Transport ({transit_stop})', font=Font.H1, fill=ColorScheme.BLACK, halign='left', valign='top')
    transit_data = get_transit_data(transit_stop)

    line_height = Font.BODY.getsize('X')[1]
    for i, (name, scheduled, exp, to) in enumerate(get_departures(transit_data)):
        if scheduled - datetime.now().astimezone() > timedelta(minutes=120):
            break

        _y = 40 + i * (line_height + 6)
        y = max(y, _y)

        box_w, box_h = 32, line_height + 2
        w, h = Font.BODY.getsize(name)
        draw.rounded_rectangle((10, _y, 10 + box_w, _y + box_h), box_h/2, fill=ColorScheme.BLACK)
        draw.text((10 + (box_w - w)/2, _y), name, font=Font.BODY, fill=ColorScheme.WHITE)

        draw.text((50, _y), to, font=Font.BODY, fill=ColorScheme.BLACK)

        if exp:
            delay = int((exp - scheduled).total_seconds() / 60)
            delay_str = f'{delay:+}\''
        else:
            delay_str = ''
        draw_time_with_delay(draw, f'{scheduled:%H:%M}', delay_str, (380, _y))

    y += line_height + section_gap

    # Weather info right now
    coords = transit_data['station']['coordinate']
    weather = get_weather_raw(latitude=coords['x'], longitude=coords['y'])
    _, y = draw_text(draw, (10, y), 'Weather Now', font=Font.H1, fill=ColorScheme.BLACK, halign='left', valign='top')
    section_top = y + 10

    weathercode = weather['current_weather']['weathercode']
    offset_now = next(
        i for i, v in enumerate(weather['hourly']['time'])
        if date_or_none(v) >= datetime.now()
    )
    current_humidity = weather['hourly']['relativehumidity_2m'][offset_now]
    current_temp = weather['current_weather']['temperature']
    icon = get_icon_for_weathercode(weathercode, 'day')
    _x, y = draw_image(
        draw,
        (10, section_top + 3),
        icon,
        fill=ColorScheme.BLACK,
        valign='top',
        halign='left',
    )
    _x1, _y = draw_text(
        draw,
        (_x + 10, section_top + 3),
        f'{current_temp:.1f}°C',
        font=Font.BIG,
        fill=ColorScheme.BLACK,
        valign='top',
        halign='left',
    )
    _x2, _y = draw_text(
        draw,
        (_x + 10, _y + 3),
        f'{current_humidity:.1f}%',
        font=Font.BIG,
        fill=ColorScheme.BLACK,
        valign='top',
        halign='left',
    )
    _x = max(_x1, _x2) + 30
    draw_text(
        draw,
        (_x, section_top + 3),
        f'{get_description_for_weathercode(weathercode)}\n'
        f'Wind: {weather["current_weather"]["windspeed"]:.1f} m/s '
        f'({angle_to_compass(weather["current_weather"]["winddirection"])})',
        font=Font.BODY,
        valign='top',
        halign='left',
    )

    y += section_gap

    # Hourly forecast
    _, y = draw_text(draw, (10, y), 'Temperature and Precipitation', font=Font.H1, fill=ColorScheme.BLACK, halign='left', valign='top')
    chart_w, chart_h = 420, 64
    x_start = 40
    y += 15

    temps = weather['hourly']['temperature_2m']
    times = weather['hourly']['time']
    rains = weather['hourly']['rain']

    offset_now = next(
        i for i, v in enumerate(times)
        if date_or_none(v) >= datetime.now()
    )
    offset_in_24h = next(
        i for i, v in enumerate(times)
        if date_or_none(v) - datetime.now() >= timedelta(hours=24)
    )
    times = times[offset_now:offset_in_24h]
    temps = temps[offset_now:offset_in_24h]
    rains = rains[offset_now:offset_in_24h]

    temp_min, temp_max = min(temps), max(temps)
    rain_max = max(rains) or 0.1

    def scale_temp(temp):
        return (temp - temp_min) / (temp_max - temp_min) * chart_h

    def scale_rain(rain):
        return rain / rain_max * chart_h

    def scale_x(i):
        return i * chart_w / len(temps)

    # Draw charts
    xs = [x_start + scale_x(i) for i in range(len(temps))]
    for x, rain in zip(xs, rains):
        if not rain:
            continue
        rain_h = y + chart_h - scale_rain(rain)
        draw.rectangle((x, rain_h, x + 5, y + chart_h), fill=ColorScheme.BLACK)

    temps = [y + chart_h - scale_temp(t) for t in temps]
    draw.line(list(zip(xs, temps)), fill=ColorScheme.ACCENT, width=3)

    char_half = Font.BODY.getsize('X')[1] / 2
    # Temp min max legend
    draw.text((10, y - char_half), f'{temp_max:.0f}°', font=Font.BODY, fill=ColorScheme.ACCENT)
    draw.text((10, y + chart_h - char_half), f'{temp_min:.0f}°', font=Font.BODY, fill=ColorScheme.ACCENT)
    # Precipitation legend
    draw_text(draw, (470, y - char_half), f'{rain_max:.1f} mm', font=Font.BODY, fill=ColorScheme.BLACK, halign='right', valign='top')
    draw_text(draw, (470, y + chart_h - char_half), f'0', font=Font.BODY, fill=ColorScheme.BLACK, halign='right', valign='top')

    _y = y
    for i, t in enumerate(times):
        if i % (len(temps) / 6) == 0:
            t = date_or_none(t)
            _, _y = draw_text(
                draw,
                (x_start + scale_x(i), y + 12 + chart_h),
                f'{t:%H:%M}',
                font=Font.BODY, fill=ColorScheme.BLACK,
                halign='left', valign='top',
            )

    y = _y + section_gap

    # Daily forecast
    _, y = draw_text(draw, (10, y), 'Weather This Week', font=Font.H1, fill=ColorScheme.BLACK, halign='left', valign='top')
    cell_w = 460 / 7
    for i, weathercode in enumerate(weather['daily']['weathercode']):
        if i > 7:
            break
        x = 10 + i * cell_w
        x_mid = int(x + cell_w / 2)

        date = date_or_none(weather['daily']['time'][i])
        _, _y = draw_text(draw, (x_mid, y + 10), f'{date:%a}', valign='top')

        icon = get_icon_for_weathercode(weathercode, 'day')
        _, _y = draw_image(
            draw,
            (x_mid, _y + 3),
            icon,
            fill=ColorScheme.BLACK,
            valign='top',
        )

        hi = f'{weather["daily"]["temperature_2m_max"][i]:.0f}'
        lo = f'{weather["daily"]["temperature_2m_min"][i]:.0f}'
        _, _ = draw_text(draw, (x_mid - 2, _y + 2), f'{hi}°', valign='top', halign='right')
        _, _y = draw_text(draw, (x_mid + 2, _y + 2), f'{lo}°', fill=ColorScheme.ACCENT, valign='top', halign='left')

    if flip:
        im = im.rotate(180, expand=False)

    display_show(im, output)


@entrypoint.command('clear')
@click.option(
    '-o', '--output', type=click.Choice(['pil', 'epd']),
    default='pil',
    help='Which display to clear',
)
def clear(output):
    display_clear(output)
