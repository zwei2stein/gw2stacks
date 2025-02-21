from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceJustDeleteUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_advice_just_delete()

    def config(self):
        self.icon = 'delete_sweep'
        self.name = 'Just delete these items'
        self.description = 'Just takes up space and has no uses, typically items from older style collections.'
