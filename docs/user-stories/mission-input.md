# Mission Input — Story Bundle

Domain: `INPUT` (Mission Input). Domain terms follow the Glossary (Ch. 12): a `Validation Error` is raised by the `Validator` before any Simulation runs; a Command String is parsed into a Command List of `F`, `L`, `R`.

---

## INPUT-STORY-001 — Reject invalid mission input

**AS A** Mission Operator
**I WANT** invalid input (unknown command, Start Position outside the Grid or on an Obstacle, empty Grid) to be rejected with a clear error
**SO THAT** I never get a result for a meaningless mission

**Architecture:** FR-7 (Ch. 1.2) · Validator and FastAPI Route Adapter (Ch. 5.2) · Runtime scenario 6.3 · Input validation and error handling (Ch. 8.1–8.2) · ADR-003 · QR-01, QR-03
**Priority:** 3 · Supporting
**Depends on:** NAV-STORY-001 for the FastAPI Route Adapter, container and logger; the Validator itself is independent (Ch. 5.2, ADR-003, QR-03)
**Implementation order:** reuse NAV-INFRA-001.1 / NAV-INFRA-001.2 with the added scenarios below → INPUT-BE-001.1 → INPUT-BE-001.2 → end-to-end scenarios below

### SCENARIO 1: An unknown command character is rejected

**Scenario ID**: INPUT-STORY-001-S1

**GIVEN**
* The Rover Service is running
* A 3 × 3 grid with no obstacles
* The rover starts at `(0, 0)` heading `N`
* The Command String is `"FFX"`

**WHEN**
* I send `POST /simulate` with `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "FFX"}`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string containing `"X"`
* The body has no `position`, `heading` or `blocked` fields

### SCENARIO 2: A Start Position on an Obstacle is rejected

**Scenario ID**: INPUT-STORY-001-S2

**GIVEN**
* The Rover Service is running
* A 3 × 3 grid with one obstacle at `(1, 1)`
* The rover starts at `(1, 1)` heading `N`
* The Command String is `"F"`

**WHEN**
* I send `POST /simulate` with `{"start": {"x": 1, "y": 1, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": [{"x": 1, "y": 1}]}, "commands": "F"}`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string
* The body has no `position`, `heading` or `blocked` fields

### SCENARIO 3: An empty Grid is rejected

**Scenario ID**: INPUT-STORY-001-S3

**GIVEN**
* The Rover Service is running
* A Grid with `width` `0` and `height` `5`, with no obstacles
* The rover starts at `(0, 0)` heading `N`
* The Command String is `"F"`

**WHEN**
* I send `POST /simulate` with `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 0, "height": 5, "obstacles": []}, "commands": "F"}`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string
* The body has no `position`, `heading` or `blocked` fields

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

#### INPUT-BE-001.1 — Validator rejects each invalid input class

**AS A** developer
**I WANT** `Validator.validate(request)` to raise `ValidationError` for the four FR-7 checks
**SO THAT** no invalid Simulation Request reaches the Command Executor

**Architecture:** Validator (Ch. 5.2) · FR-7 · Ch. 8.1 · ADR-003 · QR-03 · Glossary: Validation Error (Ch. 12)

##### SCENARIO 1: An unknown command character raises ValidationError

**Scenario ID**: INPUT-BE-001.1-S1

**GIVEN**
* A `SimulationRequest` with start `(0, 0)`, heading `N`, a 3 × 3 grid with no obstacles, commands `"FLX"`

**WHEN**
* The Validator validates the request

**THEN**
* A `ValidationError` is raised
* Its `message` is a non-empty string containing `"X"`

##### SCENARIO 2: A Start Position outside the Grid raises ValidationError

**Scenario ID**: INPUT-BE-001.1-S2

**GIVEN**
* A `SimulationRequest` with start `(3, 0)`, heading `N`, a 3 × 3 grid with no obstacles, commands `""`

**WHEN**
* The Validator validates the request

**THEN**
* A `ValidationError` is raised because `x` `3` is not less than `width` `3` (Ch. 8.1)
* Its `message` is a non-empty string

##### SCENARIO 3: A Start Position on an Obstacle raises ValidationError

**Scenario ID**: INPUT-BE-001.1-S3

**GIVEN**
* A `SimulationRequest` with start `(1, 1)`, heading `N`, a 3 × 3 grid with an obstacle at `(1, 1)`, commands `""`

**WHEN**
* The Validator validates the request

**THEN**
* A `ValidationError` is raised
* Its `message` is a non-empty string

##### SCENARIO 4: An empty Grid raises ValidationError

**Scenario ID**: INPUT-BE-001.1-S4

**GIVEN**
* A `SimulationRequest` with start `(0, 0)`, heading `N`, a grid with `width` `0`, `height` `5`, no obstacles, commands `"F"`

**WHEN**
* The Validator validates the request

**THEN**
* A `ValidationError` is raised because `width` `0` is less than `1` (Ch. 8.1)
* Its `message` is a non-empty string

##### SCENARIO 5: An empty Command List is valid and does not raise

**Scenario ID**: INPUT-BE-001.1-S5

**GIVEN**
* A `SimulationRequest` with start `(0, 0)`, heading `N`, a 3 × 3 grid with no obstacles, commands `""`

**WHEN**
* The Validator validates the request

**THEN**
* `validate` returns `None`
* No exception is raised

---

#### INPUT-BE-001.2 — Route Adapter maps ValidationError to HTTP 400

**AS A** Mission Operator
**I WANT** a `ValidationError` to become an HTTP 400 JSON body with an `error` field and no simulation result
**SO THAT** I get a clear rejection instead of a meaningless result

**Architecture:** FastAPI Route Adapter (Ch. 5.2) · Runtime scenario 6.3 · Ch. 8.1–8.2 · CV-5 · ADR-007 · QR-08

##### SCENARIO 1: An invalid Command String returns 400 and never executes commands

**Scenario ID**: INPUT-BE-001.2-S1

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`
* A spy replaces the Command Executor's `execute` method and counts calls

**WHEN**
* I post `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "FFX"}` to `/simulate`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string containing `"X"`
* The spy recorded zero calls to `execute`

##### SCENARIO 2: A Start Position outside the Grid returns 400

**Scenario ID**: INPUT-BE-001.2-S2

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`

**WHEN**
* I post `{"start": {"x": 3, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "F"}` to `/simulate`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string
* The body has no `position`, `heading` or `blocked` fields

##### SCENARIO 3: An empty Grid returns 400

**Scenario ID**: INPUT-BE-001.2-S3

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`

**WHEN**
* I post `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 0, "height": 5, "obstacles": []}, "commands": "F"}` to `/simulate`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string
* The body has no `position`, `heading` or `blocked` fields

##### SCENARIO 4: An empty Command String is still a valid request

**Scenario ID**: INPUT-BE-001.2-S4

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`

**WHEN**
* I post `{"start": {"x": 3, "y": 1, "heading": "W"}, "grid": {"width": 5, "height": 5, "obstacles": []}, "commands": ""}` to `/simulate`

**THEN**
* The response status is `200`
* The body is `{"position": {"x": 3, "y": 1}, "heading": "W", "blocked": []}`

---

### Infrastructure sub-stories

Reused from NAV-STORY-001 — no new deployment or logging infrastructure is introduced.

**Reused `NAV-INFRA-001.1` — Dockerfile + docker-compose.yml starting the Rover Service. Architecture: Ch. 7.1–7.3, TC-2, TC-3, ADR-009.**

##### ADDITIONAL SCENARIO S4: An invalid request gets 400 from the localhost container port

**Scenario ID**: NAV-INFRA-001.1-S4

**GIVEN**
* The service was started with `docker compose up -d` as in NAV-INFRA-001.1

**WHEN**
* I `POST http://127.0.0.1:8000/simulate` with the body from INPUT-STORY-001-S1

**THEN**
* The response status is `400`
* The response body has exactly one field `error`, whose value is a non-empty string containing `"X"`
* A valid request sent immediately afterwards still returns `200`

**Reused `NAV-INFRA-001.2` — one structured JSON log entry per request. Architecture: Ch. 8.3, TC-6, QR-08, QR-09, ADR-005.**

##### ADDITIONAL SCENARIO S3: A rejected request logs one WARNING entry

**Scenario ID**: NAV-INFRA-001.2-S3

**GIVEN**
* The Rover Service is running in Docker
* The current number of lines in `docker logs` is recorded

**WHEN**
* I send one `POST /simulate` request with the body from INPUT-STORY-001-S1

**THEN**
* `docker logs` shows exactly one new JSON log line for that request
* The entry has `level` `"WARNING"`, `event` `"validation_error"`, a `request_id`, `grid` `{"width": 3, "height": 3, "obstacle_count": 0}`, `start` `{"x": 0, "y": 0, "heading": "N"}`, `command_count` `3`, `result` `null`, `error` as a non-empty string containing `"X"` and a numeric `duration_ms`

Not applicable - no data store: rejected Simulation Requests are logged and answered with HTTP 400, but nothing is persisted (ADR-001, TC-4, Ch. 4.1).
Not applicable - no events: rejections are returned synchronously in the `POST /simulate` response; no message broker is involved (ADR-007, Ch. 3.2).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| INPUT-STORY-001-S1 | INPUT-STORY-001 | FR-7; Ch. 6.3; Ch. 8.1 | status `400`, one `error` field containing `"X"`, no result fields |
| INPUT-STORY-001-S2 | INPUT-STORY-001 | FR-7; Ch. 8.1; Ch. 12 Start Position | status `400`, `error` string, no result fields |
| INPUT-STORY-001-S3 | INPUT-STORY-001 | FR-7; Ch. 8.1; Ch. 12 Grid | status `400`, `error` string, no result fields |
| INPUT-BE-001.1-S1 | INPUT-BE-001.1 → INPUT-STORY-001 | Ch. 5.2 Validator; ADR-003; Ch. 8.1 | `ValidationError` with non-empty `message` containing `"X"` |
| INPUT-BE-001.1-S2 | INPUT-BE-001.1 → INPUT-STORY-001 | Ch. 8.1 Start outside grid | `ValidationError` for `x` `3` ≥ `width` `3` |
| INPUT-BE-001.1-S3 | INPUT-BE-001.1 → INPUT-STORY-001 | Ch. 8.1 Start on obstacle; ADR-003 | `ValidationError` for `(1, 1)` on obstacle |
| INPUT-BE-001.1-S4 | INPUT-BE-001.1 → INPUT-STORY-001 | Ch. 8.1 Empty grid | `ValidationError` for `width` `0` < `1` |
| INPUT-BE-001.1-S5 | INPUT-BE-001.1 → INPUT-STORY-001 | Ch. 8.1 Contract; QR-03 | `validate` returns `None`, no exception |
| INPUT-BE-001.2-S1 | INPUT-BE-001.2 → INPUT-STORY-001 | Ch. 6.3; Ch. 8.1–8.2; ADR-007 | status `400`, `error` contains `"X"`, `execute` called zero times |
| INPUT-BE-001.2-S2 | INPUT-BE-001.2 → INPUT-STORY-001 | Ch. 5.2 Route Adapter; FR-7 | status `400`, `error` field only |
| INPUT-BE-001.2-S3 | INPUT-BE-001.2 → INPUT-STORY-001 | Ch. 8.1; CV-5 | status `400`, `error` field only |
| INPUT-BE-001.2-S4 | INPUT-BE-001.2 → INPUT-STORY-001 | Ch. 8.1 Contract; ADR-004 | status `200`, unchanged `(3, 1)`/`W`, empty `blocked` |
| NAV-INFRA-001.1-S4 | NAV-INFRA-001.1 → INPUT-STORY-001 (reused) | Ch. 7.1–7.3; ADR-009 | `400` on `127.0.0.1:8000`, next valid request `200` |
| NAV-INFRA-001.2-S3 | NAV-INFRA-001.2 → INPUT-STORY-001 (reused) | Ch. 8.3; QR-08, QR-09; ADR-005 | one WARNING log line with `validation_error` and `result` `null` |
