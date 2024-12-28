source_names = {
    "$bank": "Account Bank",
    "$storage": "Material Storage",
    "$shared_slot": "Shared Inventory Slot"
}


class Source:

    def __init__(self, count: int, place: str, account: str):
        self.count = count
        self.place = place
        self.account = account

    def place_repr(self) -> str:
        return source_names.get(self.place, self.place)

    def __repr__(self):
        return str(self.count) + " " + self.place + "@" + self.account
