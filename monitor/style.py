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
    H1 = ImageFont.truetype('Inter-Bold', 18)
    BODY = ImageFont.truetype('Inter-Medium', 18)
    BIG = ImageFont.truetype('Inter-Medium', 26)
