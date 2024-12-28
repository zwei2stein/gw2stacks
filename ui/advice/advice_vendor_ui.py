from data.item import ItemForDisplay
from ui.advice.abstract_advice import Advice
from ui.ui_model import UiModel


class AdviceVendorUi(Advice):

    def __init__(self, ui_model: UiModel):
        super().__init__(ui_model)

    def get_data(self) -> list[ItemForDisplay]:
        return self.ui_model.model.get_vendor_advice()

    def config(self):
        self.icon = 'storefront'
        self.name = 'Sell to vendors'
