from importlib_resources import files


def get_font_path(name) -> str:
    return str(files('monitor.res.fonts') / f'{name}.otf')
