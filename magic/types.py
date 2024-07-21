from enum import StrEnum


class Action(StrEnum):
    JOIN = "join"
    SENT = "sent"
    READY = "ready"