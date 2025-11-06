
from dataclasses import dataclass
from enum import Enum


class QuestionEvaluationStatus(str, Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    COMPLETED = "completed"


@dataclass(slots=True)
class DimensionEvaluation:
    dimension: str
    verdict: str
    confidence: float
    notes: list[str]


@dataclass(slots=True)
class QuestionEvaluationResult:
    question_id: str
    status: QuestionEvaluationStatus
    overall: str
    dimensions: list[DimensionEvaluation]
