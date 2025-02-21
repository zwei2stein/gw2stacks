from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceLS3LS4IBSUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_ls3ls4ibs_advice()

    def config(self):
        self.icon = 'auto_awesome'
        self.name = 'Cleanup living story currencies'
        self.description = 'These items can be consumed to get currency stored in account valet. Beware, they are also currency for getting ascended trinkets, so consider using them to equip characters. They are also used to craft LS4 and LS4 legendary trinkets.'
