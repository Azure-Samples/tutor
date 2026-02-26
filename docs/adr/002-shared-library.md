# ADR-002: Shared Library Extraction (`tutor-lib`)

**Status:** Accepted  
**Date:** 2026-02-24  
**Deciders:** Platform Team

---

## Context

All five backend services currently duplicate significant amounts of code:

1. **Configuration / Cosmos access** — Each service has its own `config.py` and `cosmos.py` with near-identical `CosmosCRUD` implementations.
2. **Agent infrastructure** — `agents/tooling.py`, `agents/run.py`, `agents/clients.py` are duplicated across essays, questions, avatar, and upskilling.
3. **Missing `common` module** — Three services (Configuration, Questions, Upskilling) import `from common.config` and `from common.cosmos`, but the `common/` package does not exist in the repository. This is a critical runtime failure.
4. **Dependency lists** — All five `pyproject.toml` files share ~90% of the same dependencies.

The [holiday-peak-hub](https://github.com/Azure-Samples/holiday-peak-hub) reference architecture solves this with a `lib/` directory containing a shared installable package (`holiday_peak_lib`).

## Decision

**Extract a shared library** at `lib/` installed as `tutor-lib`, containing:

```
lib/
├── src/
│   └── tutor_lib/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py        # Pydantic Settings (env-based)
│       │   └── app_factory.py     # create_app() with standard middleware
│       ├── cosmos/
│       │   ├── __init__.py
│       │   ├── client.py          # Singleton CosmosClient
│       │   └── crud.py            # CosmosCRUD base class
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py            # BaseTutorAgent abstract class
│       │   ├── builder.py         # AgentBuilder (fluent API)
│       │   ├── registry.py        # AgentRegistry (discover + load)
│       │   └── foundry_client.py  # Azure AI Foundry client wrapper
│       ├── evaluation/
│       │   ├── __init__.py
│       │   └── evaluator.py       # FoundryEvaluator for agent quality
│       ├── middleware/
│       │   ├── __init__.py
│       │   ├── auth.py            # Entra ID JWT validation
│       │   ├── logging.py         # structlog request/response logging
│       │   └── errors.py          # Standardized error responses
│       └── schemas/
│           ├── __init__.py
│           ├── envelope.py        # ApiEnvelope[T] response wrapper
│           ├── student.py         # Shared student model
│           └── course.py          # Shared course model
├── tests/
│   └── ...
└── pyproject.toml
```

### Installation

Each service's `pyproject.toml` adds a path dependency:

```toml
[project]
dependencies = [
    "tutor-lib @ file:///${PROJECT_ROOT}/../lib",
    # ... service-specific deps only
]
```

In Docker builds, the lib is copied and installed first:

```dockerfile
COPY lib/ /app/lib/
RUN uv pip install --system /app/lib/
COPY apps/essays/ /app/service/
RUN uv pip install --system /app/service/
```

## Consequences

### Positive

- **Fixes critical `common` import failure** — All services import from `tutor_lib` instead of the missing `common` package.
- **Single source of truth** — Cosmos access, config, agent base classes defined once.
- **Reduced dependency drift** — Shared deps managed in one `pyproject.toml`.
- **Faster onboarding** — New services inherit all standard patterns.
- **Testable in isolation** — `lib/tests/` validates shared code independently.

### Negative

- **Coupling risk** — Changes to `tutor-lib` can break multiple services simultaneously.
- **Versioning discipline** — Must tag lib releases and run integration tests before merging.
- **Build complexity** — Docker builds must include the lib layer.

### Mitigations

- Semantic versioning for `tutor-lib` with breaking changes in major bumps.
- CI pipeline runs `lib/tests/` before any service build.
- Interface-based design (abstract classes) to minimize coupling surface.

## References

- [holiday-peak-hub `lib/` pattern](https://github.com/Azure-Samples/holiday-peak-hub/tree/feat/api-layer/lib)
- [Python Packaging: path dependencies](https://packaging.python.org/en/latest/specifications/dependency-specifiers/)
