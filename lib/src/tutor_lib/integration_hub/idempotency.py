"""Idempotency key construction for Integration Hub events."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True, slots=True, kw_only=True)
class IdempotencyKey:
    """Idempotency key for external learning events."""

    tenant_id: str
    provider: str
    provider_instance_id: str
    source_event_id: str
    event_version: str | None = None
    event_hash: str | None = None


def build_idempotency_key(
    *,
    tenant_id: str,
    provider: str,
    provider_instance_id: str,
    source_event_id: str,
    event_version: str | None = None,
    event_hash: str | None = None,
) -> str:
    """
    Build idempotency key: tenant_id + provider + provider_instance_id + source_event_id/version/hash.

    Examples:
        - tenant123|canvas|inst-456|event-789
        - tenant123|moodle|inst-001|event-555|v2
        - tenant123|caliper|inst-002|event-abc|v1|hash-def
    """
    parts = [tenant_id, provider, provider_instance_id, source_event_id]
    if event_version:
        parts.append(event_version)
    if event_hash:
        parts.append(event_hash)
    return "|".join(parts)


def hash_payload(payload: dict) -> str:
    """Create deterministic hash of payload for version-less idempotency."""
    import json

    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()[:16]
