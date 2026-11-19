# 10. Quality Requirements

This chapter translates the quality goals from Chapter 1.3 into concrete, testable
scenarios using the arc42 quality tree and ISO 25010 quality attributes. Each
scenario names the stimulus, the component that responds, and the measurable
response criterion.

## 10.1 Quality Tree

```
Quality
├── Correctness
│   ├── QR-01  All FR-4/FR-5/FR-6 scenarios pass BDD tests in CI
│   └── QR-02  Same input always produces the same output (determinism)
├── Testability
│   ├── QR-03  Domain core testable without Docker or a network
│   └── QR-04  Full test suite runs in under 60 seconds locally
├── Deployability
│   ├── QR-05  docker build succeeds from a clean checkout and the image runs locally
│   └── QR-06  CI/CD pipeline builds, tests and publishes the image to GHCR without manual steps
├── Simplicity
│   └── QR-07  No component added without a corresponding requirement
└── Observability
    ├── QR-08  Every request produces a structured log entry
    └── QR-09  Validation errors and unhandled exceptions are distinguishable in logs
```

## 10.2 Quality Scenarios

### QR-01 — BDD coverage of simulation behaviour

| Attribute | Correctness |
|-----------|-------------|
| **Stimulus** | The CI pipeline runs `pytest tests/bdd/` on every push to a PR branch. |
| **Component** | `CommandExecutor`, `Navigator`, `Validator` (exercised via BDD step definitions) |
| **Response criterion** | All scenarios in `simulate.feature` pass with no failures. The feature file covers: free movement in all four headings, left and right turns, obstacle blocking (skips and continues), boundary blocking (skips and continues), multiple blocked commands in one run, and the empty-command-list edge case. |
| **Verification** | CI build fails if any scenario fails; coverage report must include all domain modules. |

---

### QR-02 — Determinism

| Attribute | Correctness |
|-----------|-------------|
| **Stimulus** | The same `SimulationRequest` is passed to `CommandExecutor.execute` twice in the same process. |
| **Component** | `CommandExecutor`, `Navigator` |
| **Response criterion** | Both calls return an identical `SimulationResult` (same position, heading, and blocked list). No global or mutable shared state exists in the domain core. |
| **Verification** | Enforced structurally by `frozen=True` dataclasses (ADR-004) and pure functions; confirmed by a property-based test (pytest-hypothesis) if adopted. |

---

### QR-03 — Domain core testable without Docker

| Attribute | Testability |
|-----------|-------------|
| **Stimulus** | A developer runs `pytest tests/unit/domain/` on a machine with no Docker daemon and no network access. |
| **Component** | `Validator`, `CommandExecutor`, `Navigator` |
| **Response criterion** | All unit tests pass. No test imports `FastAPI`, `Uvicorn`, `boto3`, or any module from `rover.adapters`. |
| **Verification** | CI step `pytest tests/unit/domain/` runs without Docker or cloud credentials; enforced by the import boundary rule in Chapter 5.3. |

---

### QR-04 — Fast local test suite

| Attribute | Testability |
|-----------|-------------|
| **Stimulus** | A developer runs the full test suite (`pytest`) on a standard development laptop. |
| **Component** | All test modules |
| **Response criterion** | The suite completes in under 60 seconds, including BDD scenarios. |
| **Verification** | Measured in CI; a `pytest --timeout=60` guard is added to the CI workflow. |

---

### QR-05 — Reproducible image build from clean checkout

| Attribute | Deployability |
|-----------|-------------|
| **Stimulus** | The CI/CD pipeline runs `docker build` from a clean checkout on merge to `main`. |
| **Component** | `Dockerfile`, GitHub Actions workflow |
| **Response criterion** | The image builds successfully; `docker run` (or `docker compose up`) serves `POST /simulate` with a known input returning the expected result. |
| **Verification** | Smoke test step in the CI pipeline (Chapter 7.5, stage 7). |

---

### QR-06 — CI/CD pipeline runs end-to-end without manual steps

| Attribute | Deployability |
|-----------|-------------|
| **Stimulus** | A PR is merged to `main`. |
| **Component** | GitHub Actions workflow |
| **Response criterion** | The pipeline completes all stages (install, pre-commit, unit tests, BDD tests, Docker build, push to GHCR, smoke test) without human intervention. The published tag is available within 10 minutes of the merge. |
| **Verification** | GitHub Actions workflow run history; no manual step between merge and image publication. |

---

### QR-07 — No unnecessary components (YAGNI)

| Attribute | Simplicity |
|-----------|------------|
| **Stimulus** | The architecture reviewer inspects the building block view. |
| **Component** | All components in `rover/` |
| **Response criterion** | Every component and dependency in the codebase traces back to at least one functional requirement (FR-1 through FR-7) or a cross-cutting concept in Chapter 8. |
| **Verification** | Architecture review checklist; no component present in Chapter 5 that is not referenced by an FR or a cross-cutting concept. |

---

### QR-08 — Every request produces a structured log entry

| Attribute | Observability |
|-----------|--------------|
| **Stimulus** | The FastAPI Route Adapter processes any request (valid, invalid, or causing an unhandled exception). |
| **Component** | `Logger Adapter` |
| **Response criterion** | Exactly one JSON log entry appears in the container log stream (`docker logs`) for the request. The entry contains all mandatory fields defined in Chapter 8.3 (`level`, `event`, `request_id`, `grid`, `start`, `command_count`, `result`, `error`, `duration_ms`). |
| **Verification** | Route adapter unit tests assert the logger is called once per request with the correct fields; a smoke test after running the image checks that a log entry appears via `docker logs` within 5 seconds. |

---

### QR-09 — Validation errors and exceptions are distinguishable in logs

| Attribute | Observability |
|-----------|--------------|
| **Stimulus** | The system receives an invalid request (triggering `ValidationError`) and separately encounters an unhandled exception. |
| **Component** | `Logger Adapter`, `FastAPI Route Adapter` |
| **Response criterion** | The `ValidationError` log entry has `level: "WARNING"` and `event: "validation_error"`. The unhandled exception log entry has `level: "ERROR"`, `event: "unhandled_error"`, and includes the exception traceback. The two entries are distinguishable by `level` and `event` alone, without parsing the message text. |
| **Verification** | Route adapter unit tests assert the correct `level` and `event` values for each error path. |
