import logging
from dataclasses import dataclass
from enum import StrEnum
import random


logger = logging.getLogger(__name__)


class Answer(StrEnum):
    press = "нажать"


class Text(StrEnum):
    press = "нажмите"


numbers = list(range(1, 12))

question_template = "{question} {number}"
answer_template = "{action} {number}"


@dataclass
class Question:
    text: str
    answer: str


class Game:
    HIT = 5

    def __init__(
        self,
    ) -> None:
        self._questions: list[Question] = []
        self._active_questions: list[Question] = []

        self._team_health = 100

    def build(self) -> None:
        for value in numbers:
            self._questions.append(
                Question(
                    text=question_template.format(question=Text.press, number=value),
                    answer=answer_template.format(action=Answer.press, number=value),
                ),
            )
        random.shuffle(self._questions)

    def pop_question(self) -> Question:
        question = self._questions.pop()
        self._active_questions.append(question)
        return question

    def check_answer(self, answer: str) -> Question | None:
        for question in self._active_questions:
            if question.answer == answer:
                self._active_questions.remove(question)
                new_question = self.pop_question()

                return new_question

        else:
            self._team_health -= self.HIT

            logger.info(f"-{self.HIT} HP")
            logger.info(f"Team HP is {self._team_health} now")
