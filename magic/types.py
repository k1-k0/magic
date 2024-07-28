from enum import StrEnum


class Action(StrEnum):
    JOIN = "join"
    CONNECT = "connect"
    TEAM = "team"
    START = "start"
    ANSWERS = "answers"
    QUESTION = "question"
    ANSWER = "answer"
