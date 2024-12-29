from functools import lru_cache
from math import ceil

from data.item import Item, ItemForDisplay
from data.model_config import Gobble, MiscAdvice
from data.source import Source
from messaging.messaging import Listener, Messaging
from reader.gw2api import GW2Api


class Model(Listener):

    def __init__(self, apis: list[GW2Api], messaging: Messaging, include_consumables=False):
        self.messaging = messaging
        self.aborted = False
        self.is_ready = False

        self.items = dict()
        self.empty_slots = 0
        self.ecto_salvage_price = None
        self.material_storage_size = dict()

        self.include_consumables = include_consumables

        self.accounts = []

        self.apis = apis

    def init_from_api(self) -> None:
        if len(self.apis) == 0:
            return

        self.aborted = False
        for api in self.apis:
            api.aborted = False
        self.is_ready = False
        self.items = dict()
        self.material_storage_size = dict()
        self.accounts = []

        for api in self.apis:
            self.build_material_storage_size(api)
            self.build_inventory(api)
            self.accounts.append(api.account_name())

        self.build_item_info(self.apis[0])
        self.build_ecto_price(self.apis[0])
        self.is_ready = True

    def abort(self) -> None:
        for api in self.apis:
            api.abort()
        self.aborted = True
        self.is_ready = True
        self.items = dict()

    def add_item(self, item_id: str, account_bound: bool, source: Source) -> None:
        if item_id not in self.items:
            self.items[item_id] = Item(int(item_id))
        self.items[item_id].add(source)
        self.items[item_id].account_bound = account_bound

    def has_item(self, item_id: int) -> None:
        return item_id in self.items.keys() and self.items[item_id].total_count() > 0

    def build_material_storage_size(self, api: GW2Api) -> None:
        max_count = 0
        for material in api.material_storage():
            max_count = max(max_count, material['count'])
        self.material_storage_size[api.account_name()] = ceil(max_count / 250) * 250

    @staticmethod
    def is_account_bound(item):
        return 'Account' == item.get('binding', None)

    def build_inventory(self, api: GW2Api) -> None:
        self.empty_slots = 0

        self.messaging.broadcast(f"Loading characters@{api.account_name()}")
        for character_name in api.characters():
            self.messaging.broadcast(f"Loading character {character_name}@{api.account_name()}")
            for bag in api.character_inventory(character_name)['bags']:
                if bag is not None:
                    for item in bag['inventory']:
                        if item is not None:
                            self.add_item(item['id'], self.is_account_bound(item),
                                          Source(item['count'], character_name, api.account_name()))
                        else:
                            self.empty_slots = self.empty_slots + 1

        self.messaging.broadcast(f"Loading material storage@{api.account_name()}")
        for material in api.material_storage():
            self.add_item(material['id'], self.is_account_bound(material),
                          Source(material['count'], "$storage", api.account_name()))

        self.messaging.broadcast(f"Loading bank@{api.account_name()}")
        for item in api.bank():
            if item is not None:
                self.add_item(item['id'], self.is_account_bound(item),
                              Source(item['count'], "$bank", api.account_name()))
            else:
                self.empty_slots = self.empty_slots + 1

        self.messaging.broadcast(f"Loading shared slots@{api.account_name()}")
        for item in api.shared_slots():
            if item is not None:
                self.add_item(item['id'], self.is_account_bound(item),
                              Source(item['count'], "$shared_slot", api.account_name()))
            else:
                self.empty_slots = self.empty_slots + 1

    def build_item_info(self, api: GW2Api) -> None:
        appraise_item_ids = []
        self.messaging.broadcast("Loading item details")
        for item_info in api.item_info(frozenset(self.items.keys())):
            item = self.items.get(item_info['id'])

            item.name = item_info['name']
            item.icon = item_info['icon']
            item.rarity = item_info['rarity']

            if item_info['type'] not in ['Armor', 'Back', 'Gathering', 'Tool', 'Trinket', 'Weapon', 'Bag', 'Container',
                                         'Gizmo']:
                item.stackable = True
            elif self.include_consumables and item_info['type'] in ['Consumable'] and item_info['details']['type'] in [
                'Food', 'Utility']:
                item.stackable = True

            if 'SoulbindOnAcquire' in item_info['flags']:
                item.stackable = False

            if 'This item only has value as part of a collection.' == item_info.get("description", None):
                item.deletable = True

            if item_info['type'] in ['Armor', 'Back', 'Trinket', 'Weapon'] and item_info['rarity'] == 'Rare' and \
                    item_info['level'] > 77 and 'NoSalvage' not in item_info['flags']:
                item.rare_for_salvage = True
                appraise_item_ids.append(item.item_id)

        self.messaging.broadcast("Loading market prices")
        for price in api.item_prices(frozenset(appraise_item_ids)):
            self.items[price['id']].price = price['sells']['unit_price']

    def build_ecto_price(self, api: GW2Api) -> None:

        self.messaging.broadcast("Loading ecto price")
        price = api.item_price(19721)

        salvage_price = 0.10496
        ecto_chance = 0.875
        tp_tax = 0.85

        self.ecto_salvage_price = (price['sells']['unit_price'] * tp_tax * ecto_chance - salvage_price) / tp_tax

    @lru_cache(maxsize=None)
    def get_advice_stacks(self) -> list[ItemForDisplay]:
        stack_advice = []
        for item in filter(lambda list_item: len(list_item.get_advice_stacks(self.material_storage_size)) > 0,
                           self.items.values()):
            stack_advice.append(ItemForDisplay(item, sources=item.get_advice_stacks(self.material_storage_size)))
        return stack_advice

    @lru_cache(maxsize=None)
    def get_vendor_advice(self) -> list[ItemForDisplay]:
        junk = []
        for item in filter(lambda list_item: list_item.rarity == 'Junk', self.items.values()):
            junk.append(ItemForDisplay(item))
        return junk

    @lru_cache(maxsize=None)
    def get_rare_salvage_advice(self) -> list[ItemForDisplay]:
        rare_salvage_advice = []
        for item in filter(lambda list_item: list_item.rare_for_salvage, self.items.values()):
            if item.price > self.ecto_salvage_price:
                rare_salvage_advice.append(ItemForDisplay(item, advice='Salvage!'))
            else:
                rare_salvage_advice.append(ItemForDisplay(item, advice='Sell!'))
        return rare_salvage_advice

    @lru_cache(maxsize=None)
    def get_craft_luck_advice(self) -> list[ItemForDisplay]:

        luck_items = [45175, 45176, 45177]

        luck_items_advice = []

        for luck_item_id in luck_items:
            for account in self.accounts:
                if self.has_item(luck_item_id) and self.items[luck_item_id].total_count(account) > 250:
                    luck_items_advice.append(ItemForDisplay(self.items[luck_item_id],
                                                            sources=self.items[luck_item_id].get_sources_for_account(
                                                                account)))

        return luck_items_advice

    @lru_cache(maxsize=None)
    def get_advice_just_delete(self) -> list[ItemForDisplay]:
        just_delete_advice = []
        for item in filter(lambda list_item: list_item.deletable, self.items.values()):
            just_delete_advice.append(ItemForDisplay(item))
        return just_delete_advice

    @lru_cache(maxsize=None)
    def get_play_to_consume_advice(self) -> list[ItemForDisplay]:

        gameplay_consumables = {
            78758: "Trade to get bounty for bandit leader.",
            78886: "Have in inventory while defeating a bandit leader to spawn the Legendary Bandit Executioner",
            84335: "Use during a treasure hunt meta in Desert Highlands to spawn chests",
            67826: "Use in the Silverwastes after a meta completes to spawn chests. Make sure you have required keys.",
            67979: "Open a greater nightmare pod in the Silverwastes after completing meta.",
            67818: "Use during breach event in Silverwastes.",
            67780: "Open Tarnished chest in Silverwastes.",
            93407: "Use in the Drizzlewood Coast to spawn chests. Make sure you have required keys.",
            87517: "Open krait Sunken Chests to progress a Master Diver achievement.",
            48716: "Open chests in the Aetherpath of the Twilight Arbor dungeon.",

            78782: "Complete this bounty.",
            78754: "Complete this bounty.",
            78786: "Complete this bounty.",
            78784: "Complete this bounty.",
            78781: "Complete this bounty.",
            78883: "Complete this bounty.",
            78859: "Complete this bounty.",
            78988: "Complete this bounty.",
            78867: "Complete this bounty.",
            78954: "Complete this bounty.",

            71627: "Complete events in the Verdant Brink.",
            75024: "Complete events in the Auric Basin.",
            71207: "Complete events in the Tangled Depths."
        }

        play_to_consume_advices = []

        for item_id in gameplay_consumables.keys():
            if self.has_item(item_id):
                play_to_consume_advices.append(
                    ItemForDisplay(self.items[item_id], advice=gameplay_consumables[item_id]))

        return play_to_consume_advices

    @lru_cache(maxsize=None)
    def get_gobbler_advice(self) -> list[ItemForDisplay]:

        gobbles = [

            Gobble(46731, 77093, 250),  # Herta
            Gobble(46731, 66999, 50),  # Mawdrey
            Gobble(46733, 69887, 50),  # Princess
            Gobble(46735, 68369, 50),  # Star

            Gobble(83103, 83305, 25),  # Spearmarshall
        ]

        active_gobblers = []

        for gobble in gobbles:
            if self.has_item(gobble.item_id) and self.has_item(gobble.gobbler_item_id):
                for account in self.accounts:
                    if self.items[gobble.item_id].total_count(account) > self.material_storage_size[account]:
                        active_gobblers.append(ItemForDisplay(self.items[gobble.gobbler_item_id], sources=self.items[
                            gobble.gobbler_item_id].get_sources_for_account(account)))

        return active_gobblers

    def get_misc_advice(self) -> list[ItemForDisplay]:

        misc = [
            MiscAdvice(43773, 25, "Transform Quartz Crystals into a Charged Quartz Crystal at a place of power."),
            MiscAdvice(66608, 100, "Sift throught silky sand."),
            MiscAdvice(48717, 4, "Craft 'Completed Aetherkey'.")
        ]

        misc_advices = []

        for advice in misc:
            if self.has_item(advice.item_id) and self.items[advice.item_id].total_count() >= advice.min_size:
                misc_advices.append(ItemForDisplay(self.items[advice.item_id], advice=advice.text))

        return misc_advices
