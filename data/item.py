import math
from typing import List

from data.source import Source


class Item:

    def __init__(self, item_id: int):
        self.item_id = item_id
        self.sources = []

        self.account_bound = False
        self.name = None
        self.icon = None
        self.rarity = None
        self.stackable = False
        self.deletable = False
        self.rare_for_salvage = False
        self.price = None

    def add(self, source: Source) -> None:
        self.sources.append(source)

    def get_advice_stacks(self, material_storage_size: dict) -> list:
        if not self.account_bound:
            stackable_source = self.get_partial_stacks(material_storage_size)
            number_of_partial_stacks = len(stackable_source)
            number_of_stacks_consolidated = math.ceil(self.total_count() / 250)
            if self.stackable and (number_of_partial_stacks > 1
                                   and number_of_partial_stacks > number_of_stacks_consolidated):
                return stackable_source
            else:
                return []
        else:
            stackable_sources = []
            for account in material_storage_size.keys():
                stackable_source = self.get_partial_stacks({account: material_storage_size.get(account)})
                number_of_partial_stacks = len(stackable_source)
                number_of_stacks_consolidated = math.ceil(self.total_count(account) / 250)
                if self.stackable and (number_of_partial_stacks > 1
                                       and number_of_partial_stacks > number_of_stacks_consolidated):
                    stackable_sources.extend(stackable_source)
            return stackable_sources

    def get_partial_stacks(self, material_storage_size: dict) -> List[Source]:
        partial_stacks = []
        for source in self.sources:
            if source.account in material_storage_size.keys():
                if source.count < 250 or (
                        source.place == '$storage' and source.count < material_storage_size[source.account]):
                    partial_stacks.append(source)
        return partial_stacks

    def total_count(self, account=None) -> int:
        total = 0
        for source in self.sources:
            if account is None or source.account == account:
                total = total + source.count
        return total

    def get_sources_for_account(self, account) -> list[Source]:
        sources_for_account = []
        for source in self.sources:
            if source.account == account:
                sources_for_account.append(source)
        return sources_for_account

    def __repr__(self):
        return str(self.item_id) + " " + str(self.name) + " " + str(self.sources)


class ItemForDisplay:

    def __init__(self, item: Item, sources: list[Source] = None, advice: str = None):
        self.item = item
        if sources is None:
            self.sources = item.sources
        else:
            self.sources = sources
        self.advice = advice

    def __repr__(self):
        return str(self.item) + " " + str(self.advice) + " " + str(self.sources)
