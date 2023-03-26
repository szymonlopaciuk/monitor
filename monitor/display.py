from PIL import Image
from typing import Literal

from .style import ColorScheme


def display_show(quantized_im: Image, output: Literal['epd', 'pil']):
    if output == 'pil':
        quantized_im.show()
        return

    if output == 'epd':
        from waveshare_epd.epd7in5b_V2 import EPD  # noqa
        epd = EPD()
        epd.init()
        epd.Clear()

        black = quantized_im.point(lambda px: px != ColorScheme.BLACK, mode='1')
        red = quantized_im.point(lambda px: px != ColorScheme.ACCENT, mode='1')
        epd.show(epd.getbuffer(black), epd.getbuffer(red))
        epd.sleep()


def display_clear(output):
    if output == 'pil':
        return

    if output == 'epd':
        from waveshare_epd.epd7in5b_V2 import EPD  # noqa
        epd = EPD()
        epd.init()
        epd.Clear()
        epd.sleep()
