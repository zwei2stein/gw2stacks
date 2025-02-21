from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceRareSalvageUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_rare_salvage_advice()

    def config(self):
        self.icon = 'recycling'
        self.name = 'Rare salvage'
        self.description = 'Is it worth it to salvage rare item for Ecto or is is more worth it to sell it on Trading post?'