import re

from nicegui import ui
from nicegui.elements.input import Input

from reader.gw2api import GW2Api, InvalidAccessToken, MissingPermission
from ui.ui_model import UiModel, ApiKeyItem
from ui.unique_label import unique_label_ui


class ApiKeysManagerUi:

    def __init__(self, ui_model: UiModel):
        self.ui_model = ui_model
        self.ui()
        ui_model.api_keys.on_change = self.refresh
        self.key_pattern = re.compile(
            r"^[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{20}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}$",
            re.IGNORECASE)

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
            ui.notify("API key is invalid!", type='negative')
        except MissingPermission as mp:
            ui.notify("Missing permission " + mp.permission + " in API key.", type='negative')
        item.valid = False
        item.account = None
        return item

    def add_key(self, api_key: Input):
        validated_item = self.validate_gw2_api(ApiKeyItem(api_key.value))
        if validated_item.valid:
            self.ui_model.api_keys.add(validated_item.api_key, validated_item.valid, validated_item.account)
            self.ui_model.save()
            api_key.value = ''
        else:
            ui.notify("Not valid, will not add", type='negative')

    def remove_key(self, item: ApiKeyItem):
        self.ui_model.api_keys.remove(item)
        self.ui_model.save()

    @ui.refreshable
    def api_keys_ui(self):

        if len(self.ui_model.api_keys.items) == 0:
            with ui.row():
                ui.label('No API keys in list, add at least one').classes('mx-auto')
            return

        for item in self.ui_model.api_keys.items:
            with ui.grid(columns='auto 2fr auto auto auto auto'):
                with ui.checkbox().bind_value(item, 'selected'):
                    ui.tooltip(
                        'When getting advice, only selected accounts are searched. Multiple accounts selected can be fairly slow and will produce lots of junk results from trying to merge multiple material storages.').classes(
                        'bg-green')
                ui.label(item.api_key).classes('font-medium')
                with ui.button(icon='content_copy').props('flat fab-mini color=grey').on('click',
                                                                      js_handler=f'() => navigator.clipboard.writeText("{item.api_key}")'):
                    ui.tooltip('Copy API key to clipboard.').classes('bg-green')
                unique_label_ui(item.account)
                with ui.button(on_click=lambda: self.validate_gw2_api(item), icon='how_to_reg').props(
                        'flat fab-mini color=grey'):
                    ui.tooltip('Will validate API key with Arenanet servers.').classes('bg-green')
                with ui.button(on_click=lambda: self.remove_key(item), icon='delete').props(
                        'flat fab-mini color=grey'):
                    ui.tooltip('Remove key from list and save list.').classes('bg-green')

    def ui(self):

        self.api_keys_ui()

        with ui.grid(columns='auto auto'):
            key_input = ui.input('New GW2 API key',
                                 validation=lambda value: self.validate_gw2_api_offline(value)).style('width: 78ch')
            with ui.button(on_click=lambda: self.add_key(key_input), icon='person_add').props(
                    'flat fab-mini color=grey').bind_enabled_from(key_input, 'error', lambda error: error is None):
                ui.tooltip(
                    'Will validate API key with Arenanet servers and if okay, will add it to list and save list.').classes(
                    'bg-green')
