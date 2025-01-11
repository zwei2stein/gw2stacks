import hashlib
from functools import lru_cache

from nicegui import ui


@lru_cache
def color_hash(text: str) -> str:
    m = hashlib.md5(usedforsecurity=False)
    m.update(text.encode('utf-8'))

    digest = m.hexdigest()

    r = int(int(digest[0:2], 16) / 2) + 128
    g = int(int(digest[2:4], 16) / 2) + 128
    b = int(int(digest[4:6], 16) / 2) + 128

    return f'#{r:02x}{g:02x}{b:02x}'


def unique_label_ui(text: str) -> None:
    color = color_hash(text)
    ui.label(text).style(f'background-color: {color}').classes('h-min rounded p-1')
