from functools import lru_cache
from itertools import batched

import requests
from retrying import retry

from messaging.messaging import Listener

required_permissions = ['account', 'characters', 'inventories']

items_per_request = 200


# define Python user-defined exceptions
class InvalidAccessToken(Exception):
    pass


class MissingPermission(Exception):

    def __init__(self, permission: str):
        self.permission = permission


class Timeout(Exception):
    pass


class UserAborted(Exception):
    pass


def retry_if_timeout(exception):
    return isinstance(exception, Timeout)


def check_abort(f):
    def wrapper(*args):
        if args[0].aborted:
            raise UserAborted()
        else:
            return f(*args)

    return wrapper


class GW2Api(Listener):

    def __init__(self, api_key: str):
        self.aborted = False

        self.api_key = api_key
        self.s = requests.Session()
        self.validate()

    def validate(self) -> None:
        r = self.s.get('https://api.guildwars2.com/v2/tokeninfo', params=self.get_auth_params())

        data = r.json()

        if not r.status_code == 200:
            raise InvalidAccessToken

        if 'permissions' in data:
            for permission in required_permissions:
                if permission not in data['permissions']:
                    raise MissingPermission(permission)
        else:
            raise InvalidAccessToken

    def abort(self) -> None:
        self.aborted = True

    @staticmethod
    def verify_response(r) -> None:
        if r.status_code in (502, 504, 408):
            raise Timeout()

    def get_auth_params(self) -> list:
        return [("access_token", self.api_key)]

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def account_name(self) -> str:
        r = self.s.get('https://api.guildwars2.com/v2/account', params=self.get_auth_params())
        self.verify_response(r)
        return r.json().get("name", "?")

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def material_storage(self):
        r = self.s.get('https://api.guildwars2.com/v2/account/materials', params=self.get_auth_params())
        self.verify_response(r)
        return r.json()

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def bank(self):
        r = self.s.get('https://api.guildwars2.com/v2/account/bank', params=self.get_auth_params())
        self.verify_response(r)
        return r.json()

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def shared_slots(self):
        r = self.s.get('https://api.guildwars2.com/v2/account/inventory', params=self.get_auth_params())
        self.verify_response(r)
        return r.json()

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def characters(self):
        r = self.s.get('https://api.guildwars2.com/v2/characters', params=self.get_auth_params())
        self.verify_response(r)
        return r.json()

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def character_inventory(self, character_name: str):
        r = self.s.get(
            'https://api.guildwars2.com/v2/characters/' + requests.utils.quote(character_name) + '/inventory',
            params=self.get_auth_params())
        self.verify_response(r)
        return r.json()

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def item_info(self, item_ids: frozenset):
        item_infos = []
        for item_ids_chunk in batched(item_ids, items_per_request):
            if self.aborted:
                return None
            r = self.s.get('https://api.guildwars2.com/v2/items', params=[('ids', ",".join(map(str, item_ids_chunk)))])
            self.verify_response(r)
            item_infos.extend(r.json())
        return item_infos

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def item_prices(self, item_ids: frozenset):
        item_prices = []
        for item_ids_chunk in batched(item_ids, items_per_request):
            if self.aborted:
                return None
            r = self.s.get('https://api.guildwars2.com/v2/commerce/prices',
                           params=[('ids', ",".join(map(str, item_ids_chunk)))])
            self.verify_response(r)
            item_prices.extend(r.json())
        return item_prices

    @check_abort
    @lru_cache(maxsize=None)
    @retry(wait_fixed=200, stop_max_attempt_number=3, retry_on_exception=retry_if_timeout, wrap_exception=True)
    def item_price(self, item_id: str):
        r = self.s.get('https://api.guildwars2.com/v2/commerce/prices/' + str(item_id))
        self.verify_response(r)
        return r.json()