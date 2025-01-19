import version
from data.item import ItemForDisplay
from data.model import Model
from messaging.console_print_listener import ConsolePrintListener
from messaging.messaging import Messaging
from reader.gw2api import GW2Api

import argparse

def nice_print_advice_list(advices: list[ItemForDisplay], name: str) -> None:

    print('----------')
    print(name)
    print('----------')
    for item in advices:
        print(f"{item.item.name}")
        if item.advice:
            print(f"\tAdvice: {item.advice}")
        print("\tSources:")
        for source in item.sources:
            print(f"\t\t{source.count} {source.place}@{source.account}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GW2 inventory cleanup tool", epilog=f"Version {version.app_version}")
    parser.add_argument('api_key', metavar='API_KEY', type=str, help='GW2 Account API key')
    args = parser.parse_args()

    api = GW2Api(args.api_key)

    messaging = Messaging()
    messaging.add_listener(ConsolePrintListener())
    model = Model([api], messaging)

    model.init_from_api()

    nice_print_advice_list(model.get_advice_stacks(), "Restack")
    nice_print_advice_list(model.get_gobbler_advice(), "Gobble")
    nice_print_advice_list(model.get_vendor_advice(), "Sell to vendor")
    nice_print_advice_list(model.get_rare_salvage_advice(), "Rare salvage")
    nice_print_advice_list(model.get_craft_luck_advice(), "Craft luck")
    nice_print_advice_list(model.get_play_to_consume_advice(), "Play")
    nice_print_advice_list(model.get_advice_just_delete(), "Delete")
    nice_print_advice_list(model.get_misc_advice(), "Misc")
    nice_print_advice_list(model.get_karma_consumables_advice(), "Karma")
    nice_print_advice_list(model.get_just_salvage_advice(), "Salvage")