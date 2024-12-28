import json
import os.path
from dataclasses import dataclass, field
from queue import Queue
from typing import List, Callable

from messaging.messaging import Listener, Messaging

SAVED_MODEL_FILE = 'api_keys.json'


@dataclass
class ApiKeyItem:
    api_key: str
    selected: bool = False
    account: str = None


@dataclass
class ApiKeyList:
    on_change: Callable = None
    items: List[ApiKeyItem] = field(default_factory=list)

    def add(self, api_key: str, selected: bool = True, account: str = None) -> None:
        self.items.append(ApiKeyItem(api_key, selected, account))
        if self.on_change:
            self.on_change()

    def remove(self, item: ApiKeyItem) -> None:
        self.items.remove(item)
        if self.on_change:
            self.on_change()

    def has_key(self, value: str) -> bool:
        for item in self.items:
            if item.api_key == value:
                return True
        return False

    @property
    def is_ready(self):
        if len(self.items) == 0:
            return False
        for item in self.items:
            if item.selected:
                return True
        return False

class UiModel(Listener):

    def __init__(self):
        self.api_keys = ApiKeyList()
        self.queue = Queue()
        self.model = None
        self.model_messaging = Messaging()

    def abort(self) -> None:
        if self.model:
            self.model.abort()
        self.model_messaging.abort()

    def refresh_ui(self):
        self.model_messaging.refresh_ui()

    def clear_ui(self):
        self.model_messaging.clear_ui()

    def save(self) -> None:
        keys_list = []
        for item in self.api_keys.items:
            json_item = dict()
            json_item['api_key'] = item.api_key
            json_item['selected'] = item.selected
            json_item['account'] = item.account
            keys_list.append(json_item)
        json_data = dict()
        json_data['api_keys'] = keys_list
        with open(SAVED_MODEL_FILE, 'w') as out_file:
            file_data = json.dumps(json_data, sort_keys=True, indent=4, ensure_ascii=False)
            out_file.write(file_data)

    def restore(self) -> None:
        if os.path.isfile(SAVED_MODEL_FILE):
            with open(SAVED_MODEL_FILE, 'r') as in_file:
                json_data = json.load(in_file)
                keys_list = json_data['api_keys']
                for key in keys_list:
                    self.api_keys.add(key['api_key'], key['selected'], key['account'])