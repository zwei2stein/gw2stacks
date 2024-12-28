from colorhash import ColorHash
from nicegui import ui


def unique_label_ui(text: str) -> None:
    (ui.label(text).style(
        f'background-color: {ColorHash(text, lightness=[0.75]).hex}').classes('h-min rounded p-1'))
