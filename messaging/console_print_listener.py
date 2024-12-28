from messaging.messaging import Listener


class ConsolePrintListener(Listener):

    def listen(self, message: str) -> None:
        print(message)
