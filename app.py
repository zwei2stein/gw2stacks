from contextlib import contextmanager
from queue import Queue

from nicegui import ui, run
from nicegui.events import ClickEventArguments

import version
from data.model import Model
from log_config import logger
from messaging.console_print_listener import ConsolePrintListener
from messaging.infolog_listener import InfoLogListener
from messaging.ui_notify_listener import QueueListener
from reader.gw2api import GW2Api, InvalidAccessToken, MissingPermission, UserAborted
from ui.advice.advice_craft_ui import AdviceCraftUi
from ui.advice.advice_gobble_ui import AdviceGobbleUi
from ui.advice.advice_just_delete_ui import AdviceJustDeleteUi
from ui.advice.advice_just_salvage_ui import AdviceJustSalvageUi
from ui.advice.advice_karma_consumables_ui import AdviceKarmaConsumablesUi
from ui.advice.advice_ls3ls4ibs_ui import AdviceLS3LS4IBSUi
from ui.advice.advice_luck_craft_ui import AdviceLuckCraftUi
from ui.advice.advice_misc_ui import AdviceMiscUi
from ui.advice.advice_play_to_consume_ui import AdvicePlayToConsumeUi
from ui.advice.advice_rare_salvage_ui import AdviceRareSalvageUi
from ui.advice.advice_stacks_ui import AdviceStacksUi
from ui.advice.advice_vendor_ui import AdviceVendorUi
from ui.api_keys_manager import ApiKeysManagerUi
from ui.ui_model import UiModel


@contextmanager
def disable(button: ui.button) -> None:
    button.disable()
    try:
        yield
    finally:
        button.enable()


async def start_advice(arg: ClickEventArguments) -> None:
    with disable(ui_model.start_button):
        try:
            ui_model.busy_spinner.set_visibility(True)
            ui_model.model = None
            ui_model.clear_ui()

            if len(ui_model.api_keys.items) == 0:
                ui.notify("No api keys in list, add at least one.", type='negative')
            elif ui_model.api_keys.selected_count == 0:
                ui.notify("No api keys selected in list.", type='negative')
            else:
                api_keys = []
                for item in ui_model.api_keys.items:
                    if item.selected:
                        api_keys.append(GW2Api(item.api_key))
                ui_model.model = Model(api_keys, ui_model.model_messaging)
                ui.notify("Starting to load account data.", type='positive')
                logger.info("Starting to load account data.")
                ui_model.abort_button.set_visibility(True)
                await run.io_bound(ui_model.model.init_from_api)
                ui.notify("Account data loaded.", type='positive')
                logger.info("Account data loaded.")
        except InvalidAccessToken as iat:
            ui.notify("API key is invalid!", type='negative')
            logger.warning(f"Invalid api key {iat.api_key}")
        except MissingPermission as mp:
            ui.notify(f"Missing permission {mp.permission} in API key.", type='negative')
            logger.warning(f"Missing permission {mp.permission} in api key {mp.api_key}")
        except UserAborted:
            ui.notify("Aborted by user", type='negative')
            logger.info("User aborted a data load")
        # except Exception as e:
        #    ui.notify("Error: " + str(e), type='negative')
    ui_model.refresh_ui()
    ui_model.abort_button.set_visibility(False)
    ui_model.busy_spinner.set_visibility(False)


def notify_from_queue(queue: Queue) -> None:
    while not queue.empty():
        ui.notify(queue.get())


@ui.page('/')
def index() -> None:
    ui.page_title(f'GW2 inventory cleanup tool, v{version.app_version}')

    ui.add_head_html(
        '<link type="text/css" rel="stylesheet" href="https://d1h9a8s8eodvjz.cloudfront.net/fonts/menomonia/08-02-12/menomonia.css" />')
    ui.add_css('* { font-family: Menomonia; }')

    ui.timer(0.1, callback=lambda: notify_from_queue(ui_model.queue))

    with ui.header(elevated=True):
        with ui.row():
            ui.label('GW2 inventory cleanup tool').classes('text-xl font-medium')
            ui_model.start_button = ui.button("Advise me", icon='directions_run').props('color=green-5').classes(
                'shadow-lg').on_click(start_advice)
            ui_model.start_button.bind_enabled_from(ui_model.api_keys, 'is_ready')
            ui_model.start_button.bind_enabled_from(ui_model, 'is_ready')
            with ui_model.start_button:
                ui.tooltip(
                    'Load account info from API and populate advice. You need at least one API key in list.').classes(
                    'bg-green')
            ui_model.busy_spinner = ui.spinner('dots', size='lg', color='red')
            ui_model.busy_spinner.set_visibility(False)
            ui_model.abort_button = ui.button("Stop", icon='cancel').props('color=red-5').classes('shadow-lg').on_click(
                ui_model.abort)
            ui_model.abort_button.set_visibility(False)
            with ui_model.abort_button:
                ui.tooltip('Stop loading account info from API.').classes('bg-green')

    ApiKeysManagerUi(ui_model)

    AdviceStacksUi(ui_model)
    AdviceCraftUi(ui_model)
    AdviceGobbleUi(ui_model)
    AdviceVendorUi(ui_model)
    AdviceRareSalvageUi(ui_model)
    AdviceJustSalvageUi(ui_model)
    AdviceLuckCraftUi(ui_model)
    AdviceKarmaConsumablesUi(ui_model)
    AdvicePlayToConsumeUi(ui_model)
    AdviceLS3LS4IBSUi(ui_model)
    AdviceJustDeleteUi(ui_model)
    AdviceMiscUi(ui_model)

    with ui.footer():
        with ui.row():
            ui.label(f'Version {version.app_version}').classes('text-xs')
            ui.label('Contact me ingame at zwei.9073.').classes('text-xs')
            ui.label('Tips are welcome as well as questions').classes('text-xs')
            ui.icon('currency_bitcoin').classes('text-sm')
            ui.link('bc1qpr3ptpdjglaf9t5uhyd2cyhm7a9u4gq4l50xdu',
                    target='bitcoin:bc1qpr3ptpdjglaf9t5uhyd2cyhm7a9u4gq4l50xdu').classes('text-xs')


if __name__ in {"__main__", "__mp_main__"}:
    logger.info(f'Starting GW2 inventory cleanup tool, v{version.app_version}')

    ui_model = UiModel()
    ui_model.model_messaging.add_listener(QueueListener(ui_model.queue))
    ui_model.model_messaging.add_listener(ConsolePrintListener())
    ui_model.model_messaging.add_listener(InfoLogListener())
    ui_model.restore()

    index()

    ##ui.run()

    ui.run(native=True, fullscreen=False, reload=False)

    logger.info('Ready')
