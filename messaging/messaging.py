class Listener:

    def listen(self, message: str) -> None:
        pass

    def abort(self) -> None:
        pass

    def refresh_ui(self):
        pass

    def clear_ui(self):
        pass


class Messaging:

    def __init__(self):
        self.listeners = []

    def add_listener(self, listener: Listener) -> None:
        self.listeners.append(listener)

    def abort(self) -> None:
        for listener in self.listeners:
            listener.abort()

    def refresh_ui(self):
        for listener in self.listeners:
            listener.refresh_ui()

    def clear_ui(self):
        for listener in self.listeners:
            listener.clear_ui()

    def broadcast(self, message: str) -> None:
        for listener in self.listeners:
            listener.listen(message)
