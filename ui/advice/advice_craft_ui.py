from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceCraftUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_craft_advice()

    def config(self):
        self.icon = 'merge_type'
        self.name = 'Craft ingredients away'
        self.description = 'Craft items to get rid of stacks of ingredients. Caveat: which this can save space, it might not be economical or useful.'
