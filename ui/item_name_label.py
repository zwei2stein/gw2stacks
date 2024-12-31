from nicegui import ui

from data.item import Item

item_rarity_colors = {
    'Junk': '#AAAAAA',
    'Basic': '#000000',
    'Fine': '#62A4DA',
    'Masterwork': '#1a9306',
    'Rare': '#fcd00b',
    'Exotic': '#ffa405',
    'Ascended': '#fb3e8d',
    'Legendary': '#4C139D'
}


def item_name_label_ui(item: Item) -> None:
    color = item_rarity_colors.get(item.rarity, '#000000')

    ui.link(item.name, item.wiki_link, new_tab=True).style(
        f'color: {color}; font-weight: bold')
