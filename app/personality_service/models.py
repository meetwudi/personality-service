from typing import Any

from pydantic import BaseModel, Field


class InterrogateRequest(BaseModel):
    identifier: str = Field(description="Stable UUID identifying the graph.")
    limit: int = Field(default=3, ge=1, le=10)


class Question(BaseModel):
    text: str
    focus: str


class InterrogateResponse(BaseModel):
    identifier: str
    questions: list[Question]
    complete: bool
    export_url: str | None = None
    question_engine: str


class LearnedAnswer(BaseModel):
    question: str
    answer: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearnRequest(BaseModel):
    identifier: str = Field(description="Stable UUID identifying the graph.")
    answers: list[LearnedAnswer]


class LearnResponse(BaseModel):
    identifier: str
    learned_count: int
    complete: bool
    export_url: str
