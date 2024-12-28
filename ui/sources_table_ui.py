from typing import List

from nicegui import ui

from data.source import Source
from ui.unique_label import unique_label_ui


def sources_table_ui(sources: List[Source], account_bound_matters: bool) -> None:
    with ui.grid(columns='auto 1fr 1fr'):
        if account_bound_matters:
            ui.label('Account bound').classes('col-span-full text-sm')
        for source in sources:
            ui.label(f'{source.count:n}')
            unique_label_ui(source.place_repr())
            unique_label_ui(source.account)
