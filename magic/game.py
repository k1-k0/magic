from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import StrEnum
import random
from zoneinfo import ZoneInfo

from aiohttp.web import WebSocketResponse
from pydantic import NegativeFloat, NonNegativeFloat, PositiveFloat, PositiveInt

from magic.consts import QUESTION_TTL


logger = logging.getLogger(__name__)


class Answer(StrEnum):
    press = "нажать"


class Text(StrEnum):
    press = "нажмите"


question_template = "{question} {number}"
answer_template = "{action} {number}"


@dataclass
class Question:
    text: str
    answer: str
    sent_time: datetime | None = None

    def set_sent_time(self) -> None:
        self.sent_time = datetime.now(tz=ZoneInfo("UTC"))


class Game:
    HIT: PositiveFloat = 5.0
    QPP: PositiveInt = 5  # question per player

    def __init__(
        self,
        players: PositiveInt,
    ) -> None:
        self._players = players
        self._numbers = self._players * self.QPP

        self._questions: list[Question] = []
        self._active_questions: list[Question] = []
        self._question_2_websocket: dict[str, WebSocketResponse] = dict()

        self._answers: dict[PositiveInt, list[str]] = {i: [] for i in range(self._players)}
        self._team_health: NonNegativeFloat = 100.0

        self._prepare_game()

    @property
    def answers(self) -> dict[PositiveInt, list[str]]:
        return self._answers

    @property
    def active_questions(self) -> list[Question]:
        return self._active_questions

    @property
    def health(self) -> float:
        return self._team_health

    def _prepare_game(self) -> None:
        self._prepare_questions()
        self._prepare_answers()
        self._prepare_active_questions()

    def _prepare_questions(self) -> None:
        for value in range(1, self._numbers + 1):
            self._questions.append(
                Question(
                    text=question_template.format(question=Text.press, number=value),
                    answer=answer_template.format(action=Answer.press, number=value),
                ),
            )
        random.shuffle(self._questions)

    def _prepare_answers(self) -> None:
        i = 0
        for question in self._questions:
            if len(self._answers[i]) == self.QPP:
                i += 1

            self._answers[i].append(question.answer)

    def _prepare_active_questions(self) -> None:
        for _ in range(self._players):
            self.pop_question()

    def set_owner(self, question: str, websocket: WebSocketResponse) -> None:
        self._question_2_websocket[question] = websocket

    def get_owner(self, question: str) -> WebSocketResponse:
        return self._question_2_websocket.pop(question)

    def pop_question(self) -> Question:
        question = self._questions.pop()
        self._active_questions.append(question)

        return question

    def hit(self) -> NegativeFloat:
        self._team_health -= self.HIT
        logger.info(f"-{self.HIT} HP. Team HP is {self._team_health} now")

        return -self.HIT

    def check_answer(
        self, answer: str
    ) -> tuple[Question | None, Question | None, NegativeFloat | None]:
        for question in self._active_questions:
            if question.answer == answer:
                hit = None

                now = datetime.now(tz=ZoneInfo("UTC"))
                if now >= question.sent_time + timedelta(seconds=QUESTION_TTL):
                    logger.info(f"expired question {question=}")
                    hit = self.hit()

                old_question = question
                self._active_questions.remove(question)
                new_question = self.pop_question()

                return (old_question, new_question, hit)

        else:
            hit = self.hit()

            return (None, None, hit)
