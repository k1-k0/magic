from pydantic import BaseModel

from magic.types import Action


class Event(BaseModel):
    action: Action


class JoinEvent(Event):
    action: Action = Action.JOIN
    value: str


class ConnectEvent(Event):
    action: Action = Action.CONNECT
    value: str


class TeamEvent(Event):
    action: Action = Action.TEAM
    value: list[str]


class StartEvent(Event):
    action: Action = Action.START


class AnswersEvent(Event):
    action: Action = Action.ANSWERS
    value: list[str]


class QuestionEvent(Event):
    action: Action = Action.QUESTION
    value: str


class HitEvent(Event):
    action: Action = Action.HIT
    value: float


class FinishEvent(Event):
    action: Action = Action.FINISH
