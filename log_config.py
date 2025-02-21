import logging

def make_logger():
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    fh = logging.FileHandler('gw2_inventory_cleanup_tool.log')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    log.addHandler(fh)

    return log

logger = make_logger()