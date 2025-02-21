from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceLuckCraftUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_craft_luck_advice()

    def config(self):
        self.icon = 'casino'
        self.name = 'Craft luck away'
        self.description = 'Upgrade luck to higher tiers which take up less space or is more easily consumed.'
