from dataclasses import dataclass
from datetime import datetime
import json
import dacite
from typing import Optional


@dataclass
class HabiticaParty:
    leaderOnly: dict
    privacy: str
    memberCount: int
    balance: int
    _id: str
    type: str
    name: str
    categories: list
    leader: str
    summary: str 
    id: str

    @staticmethod
    def load(response: dict):
        return [dacite.from_dict(HabiticaParty, party) for party in response['data']]