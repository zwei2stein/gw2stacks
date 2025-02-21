from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdvicePlayToConsumeUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_play_to_consume_advice()

    def config(self):
        self.icon = 'hiking'
        self.name = 'Use up by playing the game'
        self.description = 'Items used up by playing the game, requires doing specific content and has no other use outside that.'