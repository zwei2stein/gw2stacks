from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceGobbleUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_gobbler_advice()

    def config(self):
        self.icon = 'restaurant'
        self.name = 'Gobble'
        self.description = 'These items can be consumed by gobblers to gain loot. While they have other uses (notably when crafting ascended items), they are plentiful.'
