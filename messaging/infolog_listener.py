import logging

from messaging.messaging import Listener

from log_config import logger

class InfoLogListener(Listener):

    def listen(self, message: str) -> None:
        logger.info(message)
