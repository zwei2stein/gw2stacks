from dataclasses import dataclass


@dataclass
class Gobble:
    item_id: int
    gobbler_item_id: int
    gobble_size: int

@dataclass
class MiscAdvice:
    item_id: int
    min_size: int
    text: str