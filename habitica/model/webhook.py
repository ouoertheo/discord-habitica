from .task import HabiticaDaily, HabiticaTodo, HabiticaHabit, HabiticaReward
from dataclasses import dataclass
import dacite

@dataclass
class Webhook:
    type: str
    direction: str
    delta: float
    task: HabiticaDaily | HabiticaTodo | HabiticaHabit | HabiticaReward
    user: dict
    webhookType: str

    @staticmethod
    def load(data):
        webhook = dacite.from_dict(Webhook, data)
        return webhook 