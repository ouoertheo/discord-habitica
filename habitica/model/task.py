from dataclasses import dataclass
from typing import Optional
import dacite


@dataclass
class Reminder:
    time: str
    id: str

@dataclass
class HistoryEntry:
    date: int
    value: float
    scoreUp: Optional[int]
    scoreDown: Optional[int]

@dataclass
class ChecklistItem:
    completed: bool
    text: str
    id: str

@dataclass
class Repeat:
    m: bool
    t: bool
    w: bool
    th: bool
    f: bool
    s: bool
    su: bool

@dataclass
class HabiticaTask:
    challenge: dict
    group: dict
    type: str
    notes: str
    tags: list[str]
    value: float
    priority: float
    attribute: str
    byHabitica: bool
    reminders: list[Reminder]
    createdAt: str
    updatedAt: str
    _id: str
    text: str
    userId: str
    id: str
    
@dataclass
class HabiticaTodo(HabiticaTask):
    checklist: list[ChecklistItem]

@dataclass
class HabiticaDaily(HabiticaTask):
    repeat: Repeat
    everyX: int
    streak: int
    nextDue: list
    yesterDaily: bool
    collapseChecklist: bool
    daysOfMonth: list[int]
    weeksOfMonth: list[int]
    frequency: str
    history: list[HistoryEntry]

@dataclass
class HabiticaHabit(HabiticaTask):
    up: bool
    down: bool
    counterUp: int
    counterDown: int
    frequency: str
    history: list[HistoryEntry]

@dataclass
class HabiticaReward(HabiticaTask):
    pass

@dataclass
class HabiticaTasks:
    todo: list[HabiticaTodo]
    daily: list[HabiticaDaily]
    habit: list[HabiticaHabit]
    reward: list[HabiticaReward]

    @staticmethod
    def load(response: dict):
        tasks = {"todo":[],"daily":[],"habit":[],"reward":[]}
        for task in response['data']:
            tasks[task['type']].append(task)
            
        return dacite.from_dict(HabiticaTasks, tasks)