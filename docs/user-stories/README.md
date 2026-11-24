# User Stories — Mars Rover Simulator

Stories are derived from the architecture in `architecture/` (arc42, Module 2).
Each file in this folder is a **story bundle**: one original story plus all its
FE, BE and INFRA sub-stories with GIVEN-WHEN-THEN scenarios.

## Domains (bounded contexts)

| Domain ID | Bounded context | Architecture building blocks | Architecture reference |
|-----------|-----------------|------------------------------|------------------------|
| `NAV` | **Rover Navigation** — moving and turning the rover on the grid, obstacle and boundary handling | Command Executor, Navigator, domain types (`Position`, `Heading`, `Grid`, `BlockedMove`, `SimulationResult`) | Ch. 1.2 (FR-4 – FR-6), Ch. 5.2, Ch. 6.1–6.2, ADR-002, ADR-008 |
| `INPUT` | **Mission Input** — accepting and validating a simulation request | Validator, FastAPI Route Adapter (deserialisation) | Ch. 1.2 (FR-1 – FR-3, FR-7), Ch. 6.3, Ch. 8.1, ADR-003 |
| `OPS` | **Operations** — running, observing and publishing the service | FastAPI Route Adapter (HTTP), Logger Adapter, Dockerfile / Docker Compose, GitHub Actions, GHCR | Ch. 7, Ch. 8.3, Ch. 10, ADR-005, ADR-006, ADR-007, ADR-009 |

> **Frontend:** the system has no user interface — the Mission Operator calls
> `POST /simulate` with any HTTP client. FE sub-stories are therefore *not applicable*
> in every bundle.

## Story inventory (prioritised)

Core stories (Pareto 20 %) are marked ⭐ — they deliver ~80 % of the value: without
them the simulator does not do what the kata asks.

| Priority | Story ID | Story | Core | Architecture reference | Bundle |
|----------|----------|-------|------|------------------------|--------|
| 1 | `NAV-STORY-001` | AS A Mission Operator I WANT to send a start position, heading, grid and command string and receive the rover's final position and heading SO THAT I know where the rover ends up | ⭐ | FR-1 – FR-4, FR-6; Ch. 5.2; Ch. 6.1 | [navigation.md](navigation.md) |
| 2 | `NAV-STORY-002` | AS A Mission Operator I WANT a forward move into an obstacle or off the grid to be skipped and reported with its index and reason SO THAT the rover never crashes and I know which commands were not executed | ⭐ | FR-5, FR-6; Ch. 6.2; ADR-008 | [navigation.md](navigation.md) |
| 3 | `INPUT-STORY-001` | AS A Mission Operator I WANT invalid input (unknown command, start outside the grid or on an obstacle, empty grid) to be rejected with a clear error SO THAT I never get a result for a meaningless mission | | FR-7; Ch. 6.3; Ch. 8.1 | [mission-input.md](mission-input.md) |
| 4 | `OPS-STORY-003` | AS A developer I WANT every merge to `main` to be tested, built and published to GHCR automatically SO THAT a working image is always available | | Ch. 7.5; QR-06; ADR-006 | [operations.md](operations.md) |
| 5 | `OPS-STORY-001` | AS A developer I WANT to pull and run a published GHCR image tag with one command SO THAT anyone with Docker can try the service without a cloud account | | Ch. 7.4; Ch. 7.5 (stage 7); QR-05; RISK-03; ADR-009 | [operations.md](operations.md) |
| 6 | `OPS-STORY-002` | AS A developer I WANT `ValidationError` and unhandled exceptions to be logged distinctly and unhandled exceptions to return HTTP 500 with `{"error": "internal error"}` SO THAT every failure is visible with `docker logs` and callers get the right body | | Ch. 6.3; Ch. 8.2; Ch. 8.3; QR-09; ADR-005 | — |
| 7 | `OPS-STORY-004` | AS A Mission Operator I WANT the generated OpenAPI contract to stay consistent with the domain types SO THAT clients built from `/openapi.json` do not drift from the API | | CV-5; ADR-007; RISK-02 | — |
| 8 | `INPUT-STORY-002` | AS A developer I WANT oversized request bodies to be rejected SO THAT one client cannot exhaust the container's memory | | RISK-01, RISK-04 | — |

### Why these two are core

- They implement the kata itself (FR-1 – FR-6): every other story only validates,
  runs, observes or publishes what these two produce.
- They exercise the most architecture components (Route Adapter, Command Executor,
  Navigator and all domain types).
- The two core stories depend on nothing else. `INPUT-STORY-001` depends on them
  only for the HTTP 400 mapping in the FastAPI Route Adapter; the Validator itself
  is independent (Ch. 5.2, ADR-003, QR-03). The `OPS` stories depend on the service
  the core stories create.
- `INPUT-STORY-001` is next in line because correctness is the top quality goal and
  explicitly covers FR-7 (Ch. 1.3, QR-01); it stays supporting because the Validator
  can be implemented and unit-tested without the service (QR-03).

### Acceptance criteria to carry into `NAV-STORY-002`

When the `NAV-STORY-002` bundle is written it must cover several Blocked Moves in a
single run (QR-01), the zero-based `index` with both `obstacle` and `boundary`
`reason` values (FR-5, ADR-008, Ch. 12), and continuation after each block (FR-5,
Ch. 6.2).

## Progress

📊 Pareto progress: 2/2 core stories (100 % of 20 % core stories)
🎯 Core functionality coverage: ~80 % of 80 % target

| Story | Bundle written | Implemented |
|-------|----------------|-------------|
| `NAV-STORY-001` | ✅ | ⬜ |
| `NAV-STORY-002` | ✅ | ⬜ |
| `INPUT-STORY-001` | ✅ | ⬜ |
| `OPS-STORY-001` | ✅ | ⬜ |
| `OPS-STORY-002` | ⬜ | ⬜ |
| `OPS-STORY-003` | ✅ | ⬜ |
| `OPS-STORY-004` | ⬜ | ⬜ |
| `INPUT-STORY-002` | ⬜ | ⬜ |
