# 4. Solution Strategy

This chapter maps each top-level quality goal from Chapter 1 to the architectural
decision that addresses it. Together these decisions form the solution strategy;
each one is recorded as an ADR in Chapter 9. The runtime choices below are recorded
in ADR-009, which supersedes the runtime part of ADR-001; the domain-core and
statelessness decisions in ADR-001 remain in force.

## 4.1 Strategy Overview

| Quality Goal | Architectural Decision | ADR |
|---|---|---|
| Correctness & Determinism | Pure functional domain core: given the same input the same code path always executes, with no shared state between invocations. | ADR-001 |
| Testability | Hexagonal architecture: domain core has no framework or infrastructure dependencies; it is exercised directly by pytest and pytest-bdd without Docker or a network. | ADR-001 |
| Deployability | FastAPI served by Uvicorn in a Docker container; the Dockerfile and `docker-compose.yml` define the runtime and CI/CD builds and publishes the image to GHCR. | ADR-009 (supersedes runtime part of ADR-001) |
| Simplicity | Stateless design: no database, no session, no cache; the full simulation input arrives in every request. | ADR-001 |
| Observability | Structured JSON logging written to stdout by the Logger Adapter and read with `docker logs`. | ADR-005, ADR-009 |

## 4.2 Architecture Style: Hexagonal (Ports and Adapters)

The system is divided into three concentric rings.

```
┌─────────────────────────────────────────────┐
│  Adapters (I/O boundary)                    │
│  ┌───────────────────────────────────────┐  │
│  │  Ports (contracts)                    │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Domain Core (pure Python)      │  │  │
│  │  │  - Validator                    │  │  │
│  │  │  - Navigator                    │  │  │
│  │  │  - Command Executor             │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
│  FastAPI Route Adapter │ Logger Adapter     │
└─────────────────────────────────────────────┘
```

**Domain core** — pure Python dataclasses and functions; no imports from FastAPI,
Uvicorn, or any web framework, SDK, or I/O library. Contains all simulation logic:
input validation, heading and position arithmetic, obstacle and boundary checks.
Unchanged from the serverless design.

**Ports** — Python protocols (structural interfaces) that define what the core
needs from the outside world. For the MVP there are no outbound ports because the
core does not read from or write to any external system.

**Adapters** — the FastAPI route adapter deserialises the `POST /simulate` request
body into domain types, calls the core, and serialises the result back to a JSON
response. The logger adapter wraps Python's `logging` module to emit structured
JSON to stdout.

## 4.3 Key Technology Choices

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language | Python 3.12 | Project standard; TC-1. |
| Domain modelling | `dataclasses` + plain functions | Lightweight, no ORM or DI framework needed for a stateless simulation. |
| Input validation | Manual validation in the domain `Validator` component | Keeps the validation logic inside the domain, fully testable without HTTP context; no third-party schema library added until needed. |
| HTTP runtime | FastAPI served by Uvicorn in a Docker container | Self-contained local runtime, no cloud account required; TC-2. |
| Runtime definition | `Dockerfile` + `docker-compose.yml`; CI/CD publishes the image to GHCR | TC-3; reproducible image, no cloud infrastructure-as-code tool. |
| Logging | Python `logging` → stdout → `docker logs` | Zero additional dependencies; TC-6. |
| Testing | pytest + pytest-bdd | TC-5; BDD feature files are the executable specification for FR-4 through FR-7. |

## 4.4 How the Strategy Addresses Each Requirement

| Requirement | How the strategy satisfies it |
|-------------|-------------------------------|
| FR-1 to FR-3 (inputs) | The FastAPI route adapter deserialises the JSON request body and passes them to the domain `Validator`. |
| FR-4 (command execution) | The `CommandExecutor` in the domain core iterates the command list, calling the `Navigator` for every command. |
| FR-5 (blocked F command) | `Navigator.apply` returns a `BlockedMove` when an `F` would hit an obstacle or leave the grid; the executor records the index and reason and continues. |
| FR-6 (response) | The FastAPI route adapter serialises the `SimulationResult` (final position, heading, blocked list) to JSON. |
| FR-7 (validation error) | `Validator.validate` raises a `ValidationError` before the executor is called; the route adapter maps it to an HTTP 400 response. |
