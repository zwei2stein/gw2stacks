import re

from nicegui import ui
from nicegui.elements.input import Input

from log_config import logger
from reader.gw2api import GW2Api, InvalidAccessToken, MissingPermission
from ui.ui_model import UiModel, ApiKeyItem
from ui.unique_label import unique_label_ui


class ApiKeysManagerUi:

    def __init__(self, ui_model: UiModel):
        self.ui_model = ui_model
        self.api_keys_ui()
        ui_model.api_keys.on_change = self.refresh
        self.key_pattern = re.compile(
            r"^[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{20}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}$",
            re.IGNORECASE)

        self.expanded = not self.ui_model.api_keys.selected_count > 0

    def refresh(self):
        self.api_keys_ui.refresh()

    def validate_gw2_api_offline(self, value: str) -> str | None:
        if value == '':
            return None
        if not self.key_pattern.match(value):
            return 'Does not look like it could be API key.'
        if self.ui_model.api_keys.has_key(value):
            return 'This api key was already added.'
        return None

    @staticmethod
    def validate_gw2_api(item: ApiKeyItem) -> ApiKeyItem:
        try:
            api = GW2Api(item.api_key)
            ui.notify("API key is OK.", type='positive')
            item.valid = True
            item.account = api.account_name()
            return item
        except InvalidAccessToken:
            logger.warning(f"API key {item.api_key} is invalid!")
            ui.notify("API key is invalid!", type='negative')
        except MissingPermission as mp:
            logger.warning(f"Missing permission {mp.permission} in API key {item.api_key}.")
            ui.notify(f"Missing permission {mp.permission} in API key.", type='negative')
        item.valid = False
        item.account = None
        return item

    def add_key(self, api_key: Input):
        validated_item = self.validate_gw2_api(ApiKeyItem(api_key.value))
        if validated_item.valid:
            self.ui_model.api_keys.add(validated_item.api_key, validated_item.valid, validated_item.account)
            self.ui_model.save()
            api_key.value = ''
            ui.notify(f'Added API key for {validated_item.account} account.', type='positive')
        else:
            ui.notify("Not valid, will not add", type='negative')

    def remove_key(self, item: ApiKeyItem):
        self.ui_model.api_keys.remove(item)
        self.ui_model.save()
        ui.notify(f'Deleted API key for {item.account} account.', type='info')

    def toggle_key(self):
        self.ui_model.save()
        self.api_keys_ui.refresh()

    @ui.refreshable
    def api_keys_ui(self):

        with ui.expansion(
                f"API keys (selected {self.ui_model.api_keys.selected_count}/{len(self.ui_model.api_keys.items)})",
                icon='key').classes('w-full').bind_value(self, 'expanded'):

            with ui.grid(columns='auto auto'):
                key_input = ui.input('New GW2 API key',
                                     validation=lambda value: self.validate_gw2_api_offline(value)).style(
                    'width: 78ch').props('maxlength=72')
                with ui.button(on_click=lambda: self.add_key(key_input), icon='person_add').props(
                        'flat fab-mini color=grey').bind_enabled_from(key_input, 'error', lambda error: error is None):
                    ui.tooltip(
                        'Will validate API key with Arenanet servers and if okay, will add it to list and save list.').classes(
                        'bg-green')

            if len(self.ui_model.api_keys.items) == 0:
                with ui.row():
                    ui.label('No API keys in list, add at least one').classes('mx-auto')
                return

            for item in self.ui_model.api_keys.items:
                with ui.grid(columns='auto 2fr auto auto').classes('w-full'):
                    with ui.switch().bind_value(item, 'selected').on_value_change(self.toggle_key):
                        ui.tooltip(
                            'When getting advice, only selected accounts are searched. Multiple accounts selected can be fairly slow and will produce lots of junk results from trying to merge multiple material storages.').classes(
                            'bg-green')

                    ui.label(item.api_key).classes('font-medium')

                    unique_label_ui(item.account)

                    with ui.button(icon='menu').props('flat fab-mini color=grey').classes('shadow-lg'):
                        with ui.menu():
                            with ui.menu_item().on('click',
                                                   js_handler=f'() => navigator.clipboard.writeText("{item.api_key}")'):
                                ui.icon('content_copy', color='grey').classes('size-10')
                                ui.tooltip('Copy API key to clipboard.').classes('bg-green')
                            with ui.menu_item(on_click=lambda: self.validate_gw2_api(item)):
                                ui.icon('how_to_reg', color='green').classes('size-10')
                                ui.tooltip('Will validate API key with Arenanet servers.').classes('bg-green')
                            with ui.menu_item(on_click=lambda: self.remove_key(item)):
                                ui.icon('delete', color='red').classes('size-10')
                                ui.tooltip('Remove key from list and save list.').classes('bg-green')

        ui.separator()
