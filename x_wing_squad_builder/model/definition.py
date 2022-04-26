from enum import Enum

class Statistics(Enum):
    ATTACKS = "attacks"
    ATTACK = "attack"
    ARC_TYPE = "arc_type"
    AGILITY = "agility"
    HULL = "hull"
    SHIELD = "shield"
    RECHARGE = "recharge"
    DECHARGE = "decharge"
    ENERGY = "energy"
    CHARGE = "charge"

class Attributes(Enum):
    NAME = "name"
    BASE = "base"
    ACTIONS = "actions"
    ACTION = "action"
    COLOR = "color"
    ACTION_LINK = "action_link"
    COLOR_LINK = "color_link"
    UPGRADE_SLOTS = "upgrade_slots"
    INITIATIVE = "initiative"
    LIMIT = "limit"
    COST = "cost"
    KEYWORDS = "keywords"

