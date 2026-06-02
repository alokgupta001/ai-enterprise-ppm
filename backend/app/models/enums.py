from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    PMO = "PMO"
    MANAGER = "MANAGER"
    EXECUTIVE = "EXECUTIVE"