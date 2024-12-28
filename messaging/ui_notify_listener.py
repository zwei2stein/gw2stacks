from messaging.messaging import Listener

from queue import Queue

class QueueListener(Listener):

    def __init__(self, queue: Queue):
        self.queue = queue

    def listen(self, message: str) -> None:
        self.queue.put(message)
