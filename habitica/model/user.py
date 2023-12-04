from dataclasses import dataclass, asdict
from datetime import datetime
import json
import dacite
from typing import Optional
from .task import HabiticaTasks


#############################
#######  Notification  ######
#############################
@dataclass
class Notification:
    id: str
    data: dict
    seen: bool
    type: str


###########################
#######  NewMessage  ######
###########################
@dataclass
class NewMessageNotification:
    name: str
    value: bool

##########################
#######    Tags     ######
##########################
@dataclass
class Tags:
    name: str
    id: str


##########################
#######   Profile   ######
##########################
@dataclass
class Profile:
    name: str
    blurb: Optional[str]

##########################
####### TasksOrder  ######
##########################

@dataclass 
class TasksOrder:
    habits: Optional[list]
    dailys: Optional[list]
    todos: Optional[list]
    rewards: Optional[list]

##########################
#######   Stats     ######
##########################
@dataclass
class Buffs:
    str: int
    int: int
    per: int
    con: int
    stealth: int
    streaks: bool
    snowball: bool
    spookySparkles: bool
    shinySeed: bool
    seafoam: bool

@dataclass
class Training:
    int: int
    per: int
    str: int
    con: int

@dataclass
class Stats:
    buffs: Buffs
    training: Training
    hp: float
    mp: int
    exp: int
    gp: float
    lvl: int
    character_class: str
    points: int
    str: int
    con: int
    int: int
    per: int
    toNextLevel: int
    maxHealth: int
    maxMP: int

##########################
####### Preferences ######
##########################

@dataclass
class Hair:
    color: str
    base: int
    bangs: int
    beard: int
    mustache: int
    flower: int

@dataclass
class Preferences: 
    hair: Hair
    emailNotifications: dict
    pushNotifications: dict
    suppressModals: dict
    tasks: dict
    dayStart: Optional[int]
    size: Optional[str]
    hideHeader: Optional[bool]
    skin: Optional[str]
    shirt: Optional[str]
    timezoneOffset: Optional[int]
    sound: Optional[str]
    chair: Optional[str]
    allocationMode: Optional[str]
    autoEquip: Optional[bool]
    costume: Optional[bool]
    dateFormat: Optional[str]
    sleep: Optional[bool]
    stickyHeader: Optional[bool]
    disableClasses: Optional[bool]
    newTaskEdit: Optional[bool]
    dailyDueDefaultView: Optional[bool]
    advancedCollapsed: Optional[bool]
    toolbarCollapsed: Optional[bool]
    reverseChatOrder: Optional[bool]
    developerMode: Optional[bool]
    displayInviteToPartyWhenPartyIs1: Optional[bool]
    improvementCategories: Optional[list]
    language: Optional[str]
    webhooks: Optional[dict]
    timezoneOffsetAtLastCron: Optional[int]
    background: Optional[str]
    automaticAllocation: Optional[bool]

#########################
#######    Party   ######
#########################
@dataclass
class Quest:
    progress: Optional[dict]
    RSVPNeeded: Optional[bool]

@dataclass
class Party:
    quest: Optional[Quest]
    order: str
    orderAscending: str
    _id: Optional[str]

#########################
#######    ITEMS   ######
#########################
@dataclass
class Equipped:
    armor: Optional[str]
    head: Optional[str]
    shield: Optional[str]
    weapon: Optional[str]
    body: Optional[str]
    back: Optional[str]
    headAccessory: Optional[str]
    eyewear: Optional[str]
    back: Optional[str]
    def toJson(self):
        return json.dumps(asdict(self))

@dataclass
class Costume:
    armor: Optional[str]
    head: Optional[str]
    shield: Optional[str]
    weapon: Optional[str]
    body: Optional[str]
    back: Optional[str]
    headAccessory: Optional[str]
    eyewear: Optional[str]
    back: Optional[str]
    def toJson(self):
        return json.dumps(asdict(self))

@dataclass
class Gear:
    equipped: Equipped
    costume: Costume
    owned: dict
    def toJson(self):
        return json.dumps(asdict(self))


@dataclass
class Items:
    gear: Gear
    special: dict
    lastDrop: Optional[dict]
    quests: dict
    mounts: dict
    food: dict
    hatchingPotions: dict
    eggs: dict
    pets: dict
    currentPet: Optional[str]
    currentMount: Optional[str]
    def toJson(self):
        return json.dumps(asdict(self))

@dataclass
class HistoryEntry:
    date: int | str
    value: float

#########################
#######  HISTORY   ######
#########################
@dataclass
class History:
    exp: list[HistoryEntry]
    todos: list[HistoryEntry]
    # def __post_init__(self):
    #     self.exp = [HistoryEntry(entry) for entry in self.exp]
    #     self.todos = [HistoryEntry(entry) for entry in self.todos]


#########################
#######    MAIN    ######
#########################
@dataclass
class HabiticaUser:
    achievements: dict
    backer: dict
    contributor: dict
    flags: dict
    history: History
    items: Items
    party: Party
    preferences: Preferences
    profile: Profile
    stats: Stats
    tasksOrder: TasksOrder
    _v: int
    balance: float
    _subSignature: str
    challenges: list
    guilds: list
    loginIncentives: int
    invitesSent: int
    pinnedItemsOrder: list
    lastCron: str
    newMessages: dict[str, NewMessageNotification]
    notifications: list[Notification]
    tags: list[Tags]
    newMessages: dict
    extra: dict
    webhooks: list
    pinnedItems: list
    notifications: list[Notification]
    unpinnedItems: list
    _ABTests: Optional[list]
    migration: Optional[str]
    id: str
    needsCron: bool
    tasks: Optional[HabiticaTasks]

    @staticmethod
    def load(response: dict):
        return dacite.from_dict(HabiticaUser, response['data'])