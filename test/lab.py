from enum import StrEnum

class ObjectType(StrEnum):
    APP_USER = "app_user"
    BANK = "bank"

print([a.value for a in ObjectType])
