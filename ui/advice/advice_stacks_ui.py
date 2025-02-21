from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceStacksUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_advice_stacks()

    def config(self):
        self.icon = 'widgets'
        self.name = 'Merge Stacks of items'