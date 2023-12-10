from dataclasses import dataclass

@dataclass
class AddGoldEvent:
    api_user: str
    api_token: str
    amount: int
    type: str =  "add_gold_event"

@dataclass
class AddGoldEventConfirmed:
    api_user: str
    api_token: str
    amount: int
    type: str = "add_gold_confirmed_event"