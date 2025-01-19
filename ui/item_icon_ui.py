from functools import reduce

from nicegui import ui

from data.item import ItemForDisplay

item_description_replaces = {
    '<c=@flavor>': '<i>',
    '<c>': '</i>',
    '\n': '<br/>'
}


def item_icon_ui(item: ItemForDisplay) -> None:
    with ui.image(item.item.icon).classes('w-16 h-16 shadow-lg'):
        if item.item.description:
            item_description: str = reduce(lambda a, kv: a.replace(*kv), item_description_replaces.items(),
                                           item.item.description)
            with ui.tooltip().classes('bg-transparent'):
                ui.html(item_description).classes('shadow-lg rounded bg-slate-800/75 p-1 max-w-md text-base')
