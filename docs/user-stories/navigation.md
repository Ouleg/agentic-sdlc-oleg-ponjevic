# Rover Navigation — Story Bundle

Domain: `NAV` (Rover Navigation). Coordinate convention from the Glossary (Ch. 12):
`(0, 0)` is the bottom-left cell, `N` = increasing `y`, `E` = increasing `x`.

---

## NAV-STORY-001 — Execute a command sequence [⭐ core]

**AS A** Mission Operator
**I WANT** to send a start position, heading, grid and command string and receive the rover's final position and heading
**SO THAT** I know where the rover ends up

**Architecture:** FR-1 – FR-4, FR-6 (Ch. 1.2) · Rover Service container (Ch. 5.1) · Runtime scenario 6.1 · ADR-002, ADR-009
**Priority:** 1 · Core (Pareto 20%)
**Depends on:** none
**Implementation order:** NAV-INFRA-001.1 → NAV-BE-001.1 → NAV-BE-001.2 → NAV-BE-001.3 → NAV-INFRA-001.2 → end-to-end scenarios below

### SCENARIO 1: Rover moves and turns to the expected final position

**Scenario ID**: NAV-STORY-001-S1

**GIVEN**
* The Rover Service is running
* A 5 × 5 grid with no obstacles
* The rover starts at `(0, 0)` heading `N`

**WHEN**
* I send `POST /simulate` with commands `"FFRFF"`

**THEN**
* The response status is `200`
* The final position is `(2, 2)`
* The final heading is `E`
* The `blocked` list is empty

### SCENARIO 2: Empty command string leaves the rover where it started

**Scenario ID**: NAV-STORY-001-S2

**GIVEN**
* The Rover Service is running
* A 5 × 5 grid with no obstacles
* The rover starts at `(3, 1)` heading `W`

**WHEN**
* I send `POST /simulate` with commands `""`

**THEN**
* The response status is `200`
* The final position is `(3, 1)` and the final heading is `W`
* The `blocked` list is empty

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

#### NAV-BE-001.1 — Navigator applies a single command

**AS A** developer
**I WANT** `Navigator.apply(command, position, heading, grid)` to return the new heading for `L`/`R` and the new position for `F`
**SO THAT** all rover movement rules live in one tested component

**Architecture:** Navigator (Ch. 5.2) · ADR-002 · Glossary: Turn Left, Turn Right

##### SCENARIO 1: Turning left rotates the heading anticlockwise

**Scenario ID**: NAV-BE-001.1-S1

**GIVEN**
* The rover is at `(2, 2)` heading `N` on a 5 × 5 grid

**WHEN**
* The Navigator applies command `L`

**THEN**
* The returned heading is `W`
* The position is unchanged at `(2, 2)`

##### SCENARIO 2: Four right turns bring the rover back to its original heading

**Scenario ID**: NAV-BE-001.1-S2

**GIVEN**
* The rover is at `(2, 2)` heading `N`

**WHEN**
* The Navigator applies command `R` four times, feeding each result into the next call

**THEN**
* The headings returned are `E`, `S`, `W`, `N` in that order

##### SCENARIO 3: Moving forward follows the heading

**Scenario ID**: NAV-BE-001.1-S3

**GIVEN**
* A 5 × 5 grid with no obstacles
* The rover is at `(1, 1)`

**WHEN**
* The Navigator applies command `F` once for each heading `N`, `E`, `S`, `W`

**THEN**
* The returned positions are `(1, 2)`, `(2, 1)`, `(1, 0)`, `(0, 1)` respectively
* The heading is unchanged in every case

---

#### NAV-BE-001.2 — Command Executor runs the whole command list

**AS A** developer
**I WANT** the Command Executor to call the Navigator for every command in order and return a `SimulationResult`
**SO THAT** a full command sequence produces one final position and heading

**Architecture:** Command Executor (Ch. 5.2) · Runtime scenario 6.1 · FR-4 · ADR-004 (frozen dataclasses)

##### SCENARIO 1: Commands are executed in order

**Scenario ID**: NAV-BE-001.2-S1

**GIVEN**
* A 5 × 5 grid with no obstacles
* A `SimulationRequest` with start `(0, 0)`, heading `N`, commands `F F R F F`

**WHEN**
* The Command Executor executes the request

**THEN**
* The `SimulationResult` has position `(2, 2)`, heading `E` and an empty `blocked` list

##### SCENARIO 2: The same request always gives the same result

**Scenario ID**: NAV-BE-001.2-S2

**GIVEN**
* The `SimulationRequest` from NAV-BE-001.2-S1

**WHEN**
* The Command Executor executes it twice

**THEN**
* Both `SimulationResult` objects are equal

---

#### NAV-BE-001.3 — `POST /simulate` maps JSON to the domain and back

**AS A** Mission Operator
**I WANT** the `POST /simulate` endpoint to accept my JSON request and return the result as JSON
**SO THAT** I can use the simulator from any HTTP client

**Architecture:** FastAPI Route Adapter (Ch. 5.2) · Ch. 3.2 technical context · FR-1 – FR-3, FR-6 · ADR-007

##### SCENARIO 1: Valid request returns the simulation result as JSON

**Scenario ID**: NAV-BE-001.3-S1

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`

**WHEN**
* I post `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 5, "height": 5, "obstacles": []}, "commands": "FFRFF"}` to `/simulate`

**THEN**
* The response status is `200`
* The body is `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": []}`

##### SCENARIO 2: The endpoint is described in the generated OpenAPI contract

**Scenario ID**: NAV-BE-001.3-S2

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`

**WHEN**
* I request `GET /openapi.json`

**THEN**
* The response status is `200`
* The document contains the path `/simulate` with method `post`

---

### Infrastructure sub-stories

#### NAV-INFRA-001.1 — Run the Rover Service in a Docker container

**AS A** developer
**I WANT** a `Dockerfile` and `docker-compose.yml` that start the Rover Service
**SO THAT** the simulator runs the same way on every machine without a cloud account

**Architecture:** Deployment view (Ch. 7.1–7.3) · TC-2, TC-3 · ADR-009 · RISK-01 (localhost binding)

##### SCENARIO 1: The service starts with one command

**Scenario ID**: NAV-INFRA-001.1-S1

**GIVEN**
* Docker and Docker Compose are installed
* The repository is checked out

**WHEN**
* I run `docker compose up -d`

**THEN**
* The Rover Service container is running
* `POST http://127.0.0.1:8000/simulate` with a valid request returns `200`

##### SCENARIO 2: The port is only reachable from the local machine

**Scenario ID**: NAV-INFRA-001.1-S2

**GIVEN**
* The service was started with `docker compose up -d`

**WHEN**
* I inspect the published port mapping with `docker compose port rover 8000`

**THEN**
* Port `8000` is bound to `127.0.0.1`, not `0.0.0.0`

---

#### NAV-INFRA-001.2 — One structured log entry per simulation

**AS A** developer
**I WANT** every `POST /simulate` request to write one structured JSON log entry to stdout
**SO THAT** I can see each simulation with `docker logs`

**Architecture:** Logger Adapter (Ch. 5.2) · Ch. 8.3 · QR-08 · ADR-005

##### SCENARIO 1: A successful simulation is logged once

**Scenario ID**: NAV-INFRA-001.2-S1

**GIVEN**
* The Rover Service is running in Docker

**WHEN**
* I send one valid `POST /simulate` request

**THEN**
* `docker logs` shows exactly one new JSON line for that request
* The entry has `level` `"INFO"`, a `request_id`, the final `result` and `duration_ms`

Not applicable - no data store: the service is stateless and every Simulation Request carries its full input (ADR-001, TC-4, Ch. 4.1).
Not applicable - no events: all interaction is a synchronous `POST /simulate` HTTP request/response (ADR-007, Ch. 3.2).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| NAV-STORY-001-S1 | NAV-STORY-001 | FR-4, FR-6; Ch. 6.1 | status `200`, position `(2, 2)`, heading `E`, `blocked` empty |
| NAV-STORY-001-S2 | NAV-STORY-001 | FR-4; Ch. 6.1 | position and heading unchanged |
| NAV-BE-001.1-S1 | NAV-BE-001.1 → NAV-STORY-001 | Ch. 5.2 Navigator; ADR-002 | heading `W`, position unchanged |
| NAV-BE-001.1-S2 | NAV-BE-001.1 → NAV-STORY-001 | ADR-002; Ch. 12 Turn Right | headings `E, S, W, N` |
| NAV-BE-001.1-S3 | NAV-BE-001.1 → NAV-STORY-001 | ADR-002; Ch. 12 Heading | four expected positions |
| NAV-BE-001.2-S1 | NAV-BE-001.2 → NAV-STORY-001 | Ch. 5.2 Command Executor; FR-4 | result `(2, 2)`, `E`, `[]` |
| NAV-BE-001.2-S2 | NAV-BE-001.2 → NAV-STORY-001 | QR-02; ADR-004 | two results are equal |
| NAV-BE-001.3-S1 | NAV-BE-001.3 → NAV-STORY-001 | Ch. 5.2 Route Adapter; FR-6 | status `200`, exact JSON body |
| NAV-BE-001.3-S2 | NAV-BE-001.3 → NAV-STORY-001 | CV-5; ADR-007 | `/simulate` `post` in OpenAPI |
| NAV-INFRA-001.1-S1 | NAV-INFRA-001.1 → NAV-STORY-001 | Ch. 7.1–7.3; ADR-009 | container running, `200` on localhost |
| NAV-INFRA-001.1-S2 | NAV-INFRA-001.1 → NAV-STORY-001 | RISK-01 | port bound to `127.0.0.1` |
| NAV-INFRA-001.2-S1 | NAV-INFRA-001.2 → NAV-STORY-001 | Ch. 8.3; QR-08; ADR-005 | exactly one JSON log line with required fields |

---

## NAV-STORY-002 — Report blocked moves and keep executing [⭐ core]

**AS A** Mission Operator
**I WANT** a forward move into an obstacle or off the grid to be skipped and reported with its index and reason
**SO THAT** the rover never crashes and I know which commands were not executed

**Architecture:** FR-5, FR-6 (Ch. 1.2) · Blocked Move, Index, Reason (Ch. 12) · Navigator and Command Executor (Ch. 5.2) · Runtime scenario 6.2 · ADR-008 · QR-01
**Priority:** 2 · Core (Pareto 20%)
**Depends on:** NAV-STORY-001 (reuses its Navigator, Command Executor, FastAPI Route Adapter and container)
**Implementation order:** reuse NAV-INFRA-001.1 / NAV-INFRA-001.2 with the added scenarios below → NAV-BE-002.1 → NAV-BE-002.2 → end-to-end scenarios below

### SCENARIO 1: Obstacle and boundary blocks are both reported and the run continues

**Scenario ID**: NAV-STORY-002-S1

**GIVEN**
* The Rover Service is running
* A 3 × 3 grid with one obstacle at `(1, 1)`
* The rover starts at `(0, 1)` heading `E`
* The Command String is `"FLFFRFF"`

**WHEN**
* I send `POST /simulate` with `{"start": {"x": 0, "y": 1, "heading": "E"}, "grid": {"width": 3, "height": 3, "obstacles": [{"x": 1, "y": 1}]}, "commands": "FLFFRFF"}`

**THEN**
* The response status is `200`
* The final position is `(2, 2)` and the final heading is `E`
* The `blocked` list is exactly `[{"index": 0, "reason": "obstacle"}, {"index": 3, "reason": "boundary"}]` in that order
* The `F` commands at indices `5` and `6` are executed after the boundary block at index `3` (the final `x` is `2`)

### SCENARIO 2: Several boundary blocks keep their zero-based indices in one run

**Scenario ID**: NAV-STORY-002-S2

**GIVEN**
* The Rover Service is running
* A 2 × 2 grid with no obstacles
* The rover starts at `(0, 0)` heading `W`
* The Command String is `"FFLFFRFF"`

**WHEN**
* I send `POST /simulate` with `{"start": {"x": 0, "y": 0, "heading": "W"}, "grid": {"width": 2, "height": 2, "obstacles": []}, "commands": "FFLFFRFF"}`

**THEN**
* The response status is `200`
* The final position is `(0, 0)` and the final heading is `W`
* The `blocked` list is exactly `[{"index": 0, "reason": "boundary"}, {"index": 1, "reason": "boundary"}, {"index": 3, "reason": "boundary"}, {"index": 4, "reason": "boundary"}, {"index": 6, "reason": "boundary"}, {"index": 7, "reason": "boundary"}]`
* The turns at indices `2` (`L`) and `5` (`R`) are executed between blocks (the final heading is `W`)

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

#### NAV-BE-002.1 — Navigator detects an invalid forward target

**AS A** developer
**I WANT** `Navigator.apply` to return a blocked outcome with reason `obstacle` or `boundary` when an `F` target is invalid
**SO THAT** all Blocked Move detection stays in the component that owns the movement rules

**Architecture:** Navigator (Ch. 5.2) · ADR-002 · ADR-008 · Glossary: Blocked Move, Obstacle, Boundary, Reason (Ch. 12)

##### SCENARIO 1: Forward into an obstacle is blocked

**Scenario ID**: NAV-BE-002.1-S1

**GIVEN**
* A 3 × 3 grid with an obstacle at `(1, 1)`
* The rover is at `(0, 1)` heading `E`

**WHEN**
* The Navigator applies command `F`

**THEN**
* The result is a `BlockedMove` with `reason` `"obstacle"`
* No new `Position` is returned and the rover's state remains `(0, 1)` heading `E`

##### SCENARIO 2: Forward off the grid is blocked

**Scenario ID**: NAV-BE-002.1-S2

**GIVEN**
* A 3 × 3 grid with no obstacles
* The rover is at `(0, 2)` heading `N`

**WHEN**
* The Navigator applies command `F`

**THEN**
* The result is a `BlockedMove` with `reason` `"boundary"`
* No new `Position` is returned and the rover's state remains `(0, 2)` heading `N`

##### SCENARIO 3: A turn at a grid corner never produces a BlockedMove

**Scenario ID**: NAV-BE-002.1-S3

**GIVEN**
* A 3 × 3 grid with no obstacles
* The rover is at `(2, 2)` heading `N`

**WHEN**
* The Navigator applies `L`, then applies `R` to the returned heading

**THEN**
* The returned headings are `W` then `N`
* Neither result is a `BlockedMove`

---

#### NAV-BE-002.2 — Command Executor records each block and continues

**AS A** developer
**I WANT** the Command Executor to attach the zero-based Command List index to every Blocked Move and execute the remaining commands
**SO THAT** one Simulation can report several blocks without stopping the rover

**Architecture:** Command Executor (Ch. 5.2) · FR-5, FR-6 · Runtime scenario 6.2 · ADR-008 · QR-01

##### SCENARIO 1: An obstacle block and a boundary block are both accumulated

**Scenario ID**: NAV-BE-002.2-S1

**GIVEN**
* A 3 × 3 grid with an obstacle at `(1, 1)`
* A `SimulationRequest` with start `(0, 1)`, heading `E`, commands `"FLFFRFF"` (the request from NAV-STORY-002-S1)

**WHEN**
* The Command Executor executes the request

**THEN**
* The `SimulationResult` has position `(2, 2)` and heading `E`
* Its `blocked` list is exactly `[{"index": 0, "reason": "obstacle"}, {"index": 3, "reason": "boundary"}]` in that order

##### SCENARIO 2: Indices count all commands, including skipped ones

**Scenario ID**: NAV-BE-002.2-S2

**GIVEN**
* A 2 × 2 grid with no obstacles
* A `SimulationRequest` with start `(0, 0)`, heading `W`, commands `"FFLFFRFF"` (the request from NAV-STORY-002-S2)

**WHEN**
* The Command Executor executes the request

**THEN**
* The `SimulationResult` has position `(0, 0)` and heading `W`
* Its `blocked` list is exactly `[{"index": 0, "reason": "boundary"}, {"index": 1, "reason": "boundary"}, {"index": 3, "reason": "boundary"}, {"index": 4, "reason": "boundary"}, {"index": 6, "reason": "boundary"}, {"index": 7, "reason": "boundary"}]`

---

### Infrastructure sub-stories

Reused from NAV-STORY-001 — no new deployment or logging infrastructure is introduced.

**Reused `NAV-INFRA-001.1` — Dockerfile + docker-compose.yml starting the Rover Service. Architecture: Ch. 7.1–7.3, TC-2, TC-3, ADR-009.**

##### ADDITIONAL SCENARIO S3: A blocked-move response comes back through the localhost port

**Scenario ID**: NAV-INFRA-001.1-S3

**GIVEN**
* The service was started with `docker compose up -d` as in NAV-INFRA-001.1

**WHEN**
* I `POST http://127.0.0.1:8000/simulate` with the body from NAV-STORY-002-S1

**THEN**
* The response status is `200`
* The response body is `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": [{"index": 0, "reason": "obstacle"}, {"index": 3, "reason": "boundary"}]}`

**Reused `NAV-INFRA-001.2` — one structured JSON log entry per request. Architecture: Ch. 8.3, TC-6, QR-08, ADR-005.**

##### ADDITIONAL SCENARIO S2: A run with blocks produces one INFO entry with the block count

**Scenario ID**: NAV-INFRA-001.2-S2

**GIVEN**
* The Rover Service is running in Docker
* The current number of lines in `docker logs` is recorded

**WHEN**
* I send one `POST /simulate` request with the body from NAV-STORY-002-S1

**THEN**
* `docker logs` shows exactly one new JSON log line for that request
* The entry has `level` `"INFO"`, `event` `"simulation_complete"`, a `request_id`, `grid` `{"width": 3, "height": 3, "obstacle_count": 1}`, `start` `{"x": 0, "y": 1, "heading": "E"}`, `command_count` `7`, `result` `{"x": 2, "y": 2, "heading": "E", "blocked_count": 2}`, `error` `null` and a numeric `duration_ms`

Not applicable - no data store: the two `Blocked Move` entries exist only in the in-memory `Simulation Result` returned in the HTTP response; no block history is persisted (ADR-001, TC-4, Ch. 4.1).
Not applicable - no events: blocks are returned synchronously in the `POST /simulate` response and logged to stdout, never published to a queue (ADR-007, ADR-008, Ch. 3.2).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| NAV-STORY-002-S1 | NAV-STORY-002 | FR-5, FR-6; Ch. 6.2; ADR-008 | status `200`, `(2, 2)`/`E`, blocks `[0/obstacle, 3/boundary]` |
| NAV-STORY-002-S2 | NAV-STORY-002 | FR-5; QR-01; ADR-008 | six boundary blocks at indices `0,1,3,4,6,7`, final `(0, 0)`/`W` |
| NAV-BE-002.1-S1 | NAV-BE-002.1 → NAV-STORY-002 | Ch. 5.2 Navigator; ADR-002; Ch. 12 Obstacle | `BlockedMove` reason `obstacle`, no new `Position` |
| NAV-BE-002.1-S2 | NAV-BE-002.1 → NAV-STORY-002 | Ch. 5.2 Navigator; Ch. 12 Boundary | `BlockedMove` reason `boundary`, no new `Position` |
| NAV-BE-002.1-S3 | NAV-BE-002.1 → NAV-STORY-002 | ADR-002; Ch. 12 Turn Left / Turn Right | headings `W`, `N`; no `BlockedMove` |
| NAV-BE-002.2-S1 | NAV-BE-002.2 → NAV-STORY-002 | Ch. 5.2 Command Executor; FR-5, FR-6; ADR-008 | result `(2, 2)`/`E`, two blocks with indices `0`, `3` |
| NAV-BE-002.2-S2 | NAV-BE-002.2 → NAV-STORY-002 | QR-01; ADR-008; Ch. 12 Index | six boundary blocks with zero-based indices from the full list |
| NAV-INFRA-001.1-S3 | NAV-INFRA-001.1 → NAV-STORY-002 (reused) | Ch. 7.1–7.3; ADR-009 | `200` on `127.0.0.1:8000`, exact body with two blocks |
| NAV-INFRA-001.2-S2 | NAV-INFRA-001.2 → NAV-STORY-002 (reused) | Ch. 8.3; TC-6; QR-08; ADR-005 | one INFO log line with `blocked_count` `2` |
