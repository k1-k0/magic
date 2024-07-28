import logging
from dataclasses import dataclass
from enum import StrEnum
import random


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


class Game:
    HIT = 5.0
    QPP = 5

    def __init__(
        self,
        players: int,
    ) -> None:
        self._players = players
        self._numbers = self._players * self.QPP

        self._questions: list[Question] = []
        self._active_questions: list[Question] = []

        self._answers: dict[int, list[str]] = {i: [] for i in range(self._players)}
        self._team_health: float = 100.0

        self._prepare_game()

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

    # TODO: use getter
    def answers(self) -> dict[int, list[str]]:
        return self._answers

    # TODO: use getter
    def active_questions(self) -> list[Question]:
        return self._active_questions

    # TODO: use getter
    def health(self) -> float:
        return self._team_health

    def pop_question(self) -> Question:
        question = self._questions.pop()
        self._active_questions.append(question)
        return question

    def check_answer(self, answer: str) -> tuple[Question | None, float | None]:
        for question in self._active_questions:
            if question.answer == answer:
                self._active_questions.remove(question)
                new_question = self.pop_question()

                return (new_question, None)

        else:
            self._team_health -= self.HIT

            logger.info(f"-{self.HIT} HP")
            logger.info(f"Team HP is {self._team_health} now")

            return (None, -self.HIT)
