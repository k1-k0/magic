from enum import StrEnum


class Action(StrEnum):
    JOIN = "join"
    CONNECT = "connect"
    TEAM = "team"
    START = "start"
    ANSWERS = "answers"
    QUESTION = "question"
    ANSWER = "answer"
    HIT = "hit"
    HEALTH = "health"
    FINISH = "finish"
    DISCONNECT = "disconnect"
