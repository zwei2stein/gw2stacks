from nicegui import ui

from data.item import ItemForDisplay
from messaging.messaging import Listener
from ui.item_name_label import item_name_label_ui
from ui.sources_table_ui import sources_table_ui
from ui.ui_model import UiModel


class Advice(Listener):

    def __init__(self, ui_model: UiModel):
        self.ui_model = ui_model
        ui_model.model_messaging.add_listener(self)

        self.icon: str | None = None
        self.name: str | None = None

        self.config()

        self.advice_ui()

    def config(self) -> None:
        ...

    def get_data(self) -> list:
        ...

    def refresh_ui(self) -> None:
        self.advice_ui.refresh()

    def clear_ui(self) -> None:
        self.advice_ui.refresh()

    @ui.refreshable
    def advice_ui(self) -> None:
        if not self.ui_model.model:
            with ui.expansion(self.name, icon=self.icon).classes('w-full'):
                ui.skeleton().classes('w-full')
            return

        advices: list[ItemForDisplay] = self.get_data()

        with ui.expansion(f'{self.name} ({len(advices)})', icon=self.icon, value=len(advices) > 0).classes('w-full'):
            with ui.grid(columns='auto 2fr auto').classes('w-full'):
                for item in advices:
                    ui.image(item.item.icon).classes('w-16 h-16 shadow-lg')
                    with ui.column():
                        item_name_label_ui(item.item)
                        if item.advice:
                            ui.label(item.advice)
                    sources_table_ui(item.sources, item.item.account_bound)
                    ui.separator().classes('col-span-full')

            if len(advices) == 0:
                ui.label('No advice here, all is well.')
                ui.separator().classes('col-span-full')