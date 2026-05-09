"""Integration Hub - Anti-Corruption Layer for external learning systems."""

from .contracts import (
    AttemptSubmission,
    ConnectorHealth,
    ConnectorState,
    ConnectorStatus,
    DeadLetterEntry,
    EngagementSignal,
    Enrollment,
    ExternalIdentity,
    LearningActivity,
    LearningContext,
    PerformanceResult,
)
from .idempotency import IdempotencyKey, build_idempotency_key
from .mappers import (
    CanonicalValidationError,
    canonical_to_learner_record_event,
    validate_canonical_event,
)
from .repositories import (
    ConnectorStateRepository,
    CosmosConnectorStateRepository,
    CosmosDeadLetterRepository,
    CosmosIdempotencyRepository,
    DeadLetterRepository,
    IdempotencyRepository,
    InMemoryConnectorStateRepository,
    InMemoryDeadLetterRepository,
    InMemoryIdempotencyRepository,
)

__all__ = [
    "AttemptSubmission",
    "CanonicalValidationError",
    "ConnectorHealth",
    "ConnectorState",
    "ConnectorStatus",
    "DeadLetterEntry",
    "EngagementSignal",
    "Enrollment",
    "ExternalIdentity",
    "LearningActivity",
    "LearningContext",
    "PerformanceResult",
    "IdempotencyKey",
    "build_idempotency_key",
    "canonical_to_learner_record_event",
    "validate_canonical_event",
    "ConnectorStateRepository",
    "CosmosConnectorStateRepository",
    "CosmosDeadLetterRepository",
    "CosmosIdempotencyRepository",
    "DeadLetterRepository",
    "IdempotencyRepository",
    "InMemoryConnectorStateRepository",
    "InMemoryDeadLetterRepository",
    "InMemoryIdempotencyRepository",
]
