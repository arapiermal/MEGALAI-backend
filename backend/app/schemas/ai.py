from typing import List, Optional

from pydantic import BaseModel


class LessonInput(BaseModel):
    topic: str
    grade: str
    objectives: List[str]


class Lesson(BaseModel):
    title: str
    overview: str
    objectives: List[str]
    activities: List[str]
    assessment: str


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str


class QuizInput(BaseModel):
    topic: str
    num_questions: int = 5


class Quiz(BaseModel):
    topic: str
    questions: List[QuizQuestion]


class WorksheetInput(BaseModel):
    topic: str
    grade: str


class Worksheet(BaseModel):
    topic: str
    activities: List[str]


class RubricCriterion(BaseModel):
    criterion: str
    description: str
    points: int


class RubricInput(BaseModel):
    assignment_type: str
    description: Optional[str] = None


class Rubric(BaseModel):
    assignment_type: str
    criteria: List[RubricCriterion]


class TextToolInput(BaseModel):
    mode: str
    text: str


class TextToolResult(BaseModel):
    output: str
