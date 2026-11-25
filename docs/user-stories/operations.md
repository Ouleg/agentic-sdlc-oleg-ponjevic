# Operations — Story Bundle

Domain: `OPS` (Operations). Image tags follow Ch. 7.4 and the Glossary: `ghcr.io/OWNER/rover-service:<git-sha>`, plus `latest` on `main`; the concrete SHAs `1a2b3c4`, `2b3c4d5` and `3c4d5e6` stand in for real commit IDs in the scenarios below.

---

## OPS-STORY-003 — Publish the image on every merge to main

**AS A** developer
**I WANT** every merge to `main` to be tested, built and published to GHCR automatically
**SO THAT** a working image is always available

**Architecture:** GitHub Actions and GHCR nodes (Ch. 7.2) · Image registry and access (Ch. 7.4) · Deployment pipeline stages 1–7 (Ch. 7.5) · QR-05, QR-06 (Ch. 10) · OC-4 · TC-3 · ADR-006 · ADR-009
**Priority:** 4 · Supporting
**Depends on:** NAV-STORY-001 (provides the Rover Service, `Dockerfile` and `docker-compose.yml` that the pipeline builds)
**Implementation order:** OPS-INFRA-003.1 → OPS-INFRA-003.2 → end-to-end scenarios below

### SCENARIO 1: A merge to main publishes both image tags without manual steps

**Scenario ID**: OPS-STORY-003-S1

**GIVEN**
* An approved PR was merged to `main` as commit `1a2b3c4` (OC-5)
* The GitHub Actions workflow is configured from `main`

**WHEN**
* The workflow run for commit `1a2b3c4` completes

**THEN**
* Stages 1–7 (install, pre-commit, unit tests, BDD tests, Docker build, push to GHCR, smoke test) all have status `success` in that order
* GHCR contains `ghcr.io/OWNER/rover-service:1a2b3c4` and `ghcr.io/OWNER/rover-service:latest`
* `latest` resolves to the image built from commit `1a2b3c4`
* Both tags are available within 10 minutes of the merge (QR-06)
* The run log contains no manual approval step

### SCENARIO 2: A pull request runs checks but does not publish

**Scenario ID**: OPS-STORY-003-S2

**GIVEN**
* A PR branch has passing checks and commit `2b3c4d5`

**WHEN**
* The workflow run for commit `2b3c4d5` completes

**THEN**
* Stages 1–4 and the Docker build check all have status `success`
* No `docker push` stage appears in the run log
* GHCR contains no tag `ghcr.io/OWNER/rover-service:2b3c4d5`

### SCENARIO 3: A failing test on a merge blocks publication

**Scenario ID**: OPS-STORY-003-S3

**GIVEN**
* A merge commit `3c4d5e6` has a failing test in `pytest tests/unit/`

**WHEN**
* The workflow run for commit `3c4d5e6` completes

**THEN**
* The job has status `failure` at stage 3 and stages 4–7 do not appear in the run log
* GHCR contains no tag `ghcr.io/OWNER/rover-service:3c4d5e6`
* `ghcr.io/OWNER/rover-service:latest` still resolves to the image built from commit `1a2b3c4`

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

Not applicable - no application component changes; the workflow builds and smoke-tests the existing Rover Service (Ch. 5.1, Ch. 7.5).

### Infrastructure sub-stories

#### OPS-INFRA-003.1 — GitHub Actions workflow publishes the image on merge

**AS A** developer
**I WANT** a workflow YAML that runs checks and tests, builds the image and pushes it to GHCR after a merge to `main`
**SO THAT** publishing an image tag is the automatic release action

**Architecture:** Ch. 7.2 (GitHub Actions, GHCR) · Ch. 7.4 (registry access, tags) · Ch. 7.5 stages 1–7 · TC-3 · OC-4 · ADR-006 · ADR-009 · QR-06

##### SCENARIO 1: A PR run executes stages 1–4 and a build check but no push

**Scenario ID**: OPS-INFRA-003.1-S1

**GIVEN**
* The workflow YAML is present on a PR branch with commit `2b3c4d5`
* GitHub Actions uses the automatic `GITHUB_TOKEN` scoped to `packages: write` (Ch. 7.4)

**WHEN**
* The PR workflow run finishes

**THEN**
* The run log shows `pip install -r requirements.txt`, `black`, `isort`, `ruff`, `bandit`, `detect-secrets`, `pytest tests/unit/` and `pytest tests/bdd/` with status `success`
* The run log shows `docker build -t ghcr.io/OWNER/rover-service:2b3c4d5 .` with status `success`
* The run log contains no `docker push` command
* No `ghcr.io/OWNER/rover-service:2b3c4d5` tag appears in GHCR

##### SCENARIO 2: A merge run executes all seven stages and pushes both tags

**Scenario ID**: OPS-INFRA-003.1-S2

**GIVEN**
* Commit `1a2b3c4` is on `main`
* The workflow YAML is the version on `main` (OC-5)

**WHEN**
* The merge workflow run finishes

**THEN**
* The run log shows the stages in the order 1 → 2 → 3 → 4 → 5 → 6 → 7 (Ch. 7.5)
* Stage 6 runs `docker push ghcr.io/OWNER/rover-service:1a2b3c4`
* GHCR holds `ghcr.io/OWNER/rover-service:1a2b3c4` and `ghcr.io/OWNER/rover-service:latest`
* The run log contains no AWS credentials, SAM commands or cloud IAM configuration (ADR-009)

---

#### OPS-INFRA-003.2 — Pipeline failure visibility and smoke test gate

**AS A** developer
**I WANT** the workflow run history to show failures and the published image to be smoke-tested
**SO THAT** an image is only published after all tests pass (stages 3-4 gate stage 6), and a broken published image is detected immediately by the stage 7 smoke test

**Architecture:** Ch. 7.5 stage 7 (smoke test) · QR-05 Verification, QR-06 Verification (Ch. 10) · QR-01 (BDD in CI) · ADR-006

##### SCENARIO 1: A failed unit test is visible and prevents later stages

**Scenario ID**: OPS-INFRA-003.2-S1

**GIVEN**
* Commit `3c4d5e6` contains a unit test that fails

**WHEN**
* I inspect the GitHub Actions run history for commit `3c4d5e6`

**THEN**
* The job conclusion is `failure` at stage 3 (`pytest tests/unit/`)
* No stages 4–7 appear in the run log
* No tag `ghcr.io/OWNER/rover-service:3c4d5e6` was pushed to GHCR

##### SCENARIO 2: The smoke test exercises the pushed image

**Scenario ID**: OPS-INFRA-003.2-S2

**GIVEN**
* `ghcr.io/OWNER/rover-service:1a2b3c4` was pushed to GHCR

**WHEN**
* Stage 7 runs the image and posts the request from NAV-STORY-001-S1 to `/simulate`

**THEN**
* The smoke test step conclusion is `success`
* The response status is `200`
* The asserted response body is `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": []}`

Not applicable - no simulation data store: the Rover Service is stateless; the pipeline persists only the OCI image tag in GHCR, which is covered by OPS-INFRA-003.1 (ADR-001, TC-4, Ch. 7.4).
Not applicable - no asynchronous messaging: push and PR events start the workflow but service interaction stays synchronous HTTP request/response (ADR-007, Ch. 3.2, Ch. 7.5).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| OPS-STORY-003-S1 | OPS-STORY-003 | Ch. 7.5; QR-06; ADR-006 | stages 1–7 success, both tags within 10 minutes, no manual step |
| OPS-STORY-003-S2 | OPS-STORY-003 | Ch. 7.5; ADR-006 | stages 1–4 + build only, no `:2b3c4d5` tag |
| OPS-STORY-003-S3 | OPS-STORY-003 | Ch. 7.5; QR-06; OC-4 | failure at stage 3, no push, `latest` unchanged |
| OPS-INFRA-003.1-S1 | OPS-INFRA-003.1 → OPS-STORY-003 | Ch. 7.5 stages 1–5; Ch. 7.4; ADR-006 | exact commands success, no `docker push`, no tag |
| OPS-INFRA-003.1-S2 | OPS-INFRA-003.1 → OPS-STORY-003 | Ch. 7.5 stages 5–6, Ch. 7.4; ADR-009 | stages 1→7, SHA + `latest` pushed, no cloud config |
| OPS-INFRA-003.2-S1 | OPS-INFRA-003.2 → OPS-STORY-003 | QR-06 Verification; ADR-006 | job `failure` at stage 3, stages 4–7 absent, no tag |
| OPS-INFRA-003.2-S2 | OPS-INFRA-003.2 → OPS-STORY-003 | Ch. 7.5 stage 7; QR-05 | smoke step success, status `200`, exact result body |

---

## OPS-STORY-001 — Run a published image tag locally

**AS A** developer
**I WANT** to pull and run a published GHCR image tag with one command
**SO THAT** anyone with Docker can try the service without a cloud account

**Architecture:** Infrastructure overview (Ch. 7.1–7.2) · Container configuration (Ch. 7.3) · Image registry and access (Ch. 7.4) · Smoke test (Ch. 7.5 stage 7) · Environments (Ch. 7.6) · QR-05 · RISK-03 · ADR-009 · Glossary: Published Image Tag
**Priority:** 5 · Supporting
**Depends on:** OPS-STORY-003 (publishes the tag) and NAV-STORY-001 (provides the image contents)
**Implementation order:** OPS-INFRA-001.1 → reuse NAV-INFRA-001.2 with the added scenario below → end-to-end scenarios below (no backend or frontend component changes)

### SCENARIO 1: One command pulls and starts a published tag

**Scenario ID**: OPS-STORY-001-S1

**GIVEN**
* Docker is installed on the workstation
* The tag `ghcr.io/OWNER/rover-service:1a2b3c4` is published in GHCR (OPS-STORY-003)
* The tag is not in the local image cache
* The developer has no cloud account and no GHCR credentials (public image, Ch. 7.4)

**WHEN**
* I run `docker run --rm -p 127.0.0.1:8000:8000 ghcr.io/OWNER/rover-service:1a2b3c4`

**THEN**
* The command output shows the image being pulled from GHCR and then a running container
* No `docker login`, IAM role or cloud account configuration is used
* `POST http://127.0.0.1:8000/simulate` with the body from NAV-STORY-001-S1 returns status `200`
* The response body is `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": []}`

### SCENARIO 2: The `latest` tag runs the same API

**Scenario ID**: OPS-STORY-001-S2

**GIVEN**
* `ghcr.io/OWNER/rover-service:latest` points to the image built from commit `1a2b3c4` on `main` (Ch. 7.4, Ch. 7.6)

**WHEN**
* I run `docker run --rm -p 127.0.0.1:8000:8000 ghcr.io/OWNER/rover-service:latest`

**THEN**
* The container is running and the mapped port is `127.0.0.1:8000`
* `POST http://127.0.0.1:8000/simulate` with the body from NAV-STORY-001-S1 returns status `200`
* The response body is `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": []}`

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

Not applicable - no application component changes; the published image already contains the Rover Service and its `POST /simulate` route (Ch. 5.1, ADR-009).

### Infrastructure sub-stories

#### OPS-INFRA-001.1 — Pull and run a published GHCR tag with one command

**AS A** developer
**I WANT** a single `docker run` command to pull a published tag and start the Rover Service
**SO THAT** local smoke tests use the released artefact instead of a source build

**Architecture:** Ch. 7.1–7.2 (local Docker Engine, GHCR) · Ch. 7.3 (port, Uvicorn, `LOG_LEVEL`) · Ch. 7.4 (public pull, tags) · Ch. 7.6 (Published Image Tag environment) · QR-05 · RISK-03 · ADR-009

##### SCENARIO 1: An uncached tag is pulled and started by `docker run`

**Scenario ID**: OPS-INFRA-001.1-S1

**GIVEN**
* `ghcr.io/OWNER/rover-service:1a2b3c4` is published and absent from the local image cache

**WHEN**
* I run `docker run --rm -p 127.0.0.1:8000:8000 ghcr.io/OWNER/rover-service:1a2b3c4`

**THEN**
* The command output shows the image being pulled from `ghcr.io/OWNER/rover-service:1a2b3c4`
* A container ID is printed and the container remains running
* No local `docker build` step runs

##### SCENARIO 2: A pre-pulled tag starts without a second pull

**Scenario ID**: OPS-INFRA-001.1-S2

**GIVEN**
* `docker pull ghcr.io/OWNER/rover-service:1a2b3c4` completed successfully (RISK-03 mitigation)

**WHEN**
* I run `docker run --rm -p 127.0.0.1:8000:8000 ghcr.io/OWNER/rover-service:1a2b3c4`

**THEN**
* The command output contains no `Pulling` step
* `POST http://127.0.0.1:8000/simulate` with the body from NAV-STORY-001-S1 returns status `200` and the body `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": []}`

##### SCENARIO 3: An unpublished tag does not start a container

**Scenario ID**: OPS-INFRA-001.1-S3

**GIVEN**
* No tag `ghcr.io/OWNER/rover-service:does-not-exist` exists in GHCR (Ch. 7.4 publishes only SHA tags and `latest`)

**WHEN**
* I run `docker run --rm -p 127.0.0.1:8000:8000 ghcr.io/OWNER/rover-service:does-not-exist`

**THEN**
* The command exits with a non-zero status
* No container from that tag is running
* No local image build is attempted

---

**Reused `NAV-INFRA-001.2` — one structured JSON log entry per request. Architecture: Ch. 8.3, TC-6, QR-08, ADR-005.**

##### ADDITIONAL SCENARIO S4: A request to the published image logs one JSON line

**Scenario ID**: NAV-INFRA-001.2-S4

**GIVEN**
* The container started from `ghcr.io/OWNER/rover-service:1a2b3c4` is running
* The current number of lines in `docker logs` is recorded

**WHEN**
* I send one `POST /simulate` request with the body from NAV-STORY-001-S1

**THEN**
* `docker logs` shows exactly one new JSON log line for that request
* The entry has `level` `"INFO"`, `event` `"simulation_complete"`, a `request_id`, `grid` `{"width": 5, "height": 5, "obstacle_count": 0}`, `start` `{"x": 0, "y": 0, "heading": "N"}`, `command_count` `5`, `result` `{"x": 2, "y": 2, "heading": "E", "blocked_count": 0}`, `error` `null` and a numeric `duration_ms`

Not applicable - no simulation data store: the service in the published image is stateless; every request carries its full input (ADR-001, TC-4, Ch. 4.1).
Not applicable - no events: all interaction with the published image is a synchronous `POST /simulate` HTTP request/response (ADR-007, Ch. 3.2).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| OPS-STORY-001-S1 | OPS-STORY-001 | Ch. 7.4; Ch. 7.5 stage 7; QR-05; ADR-009 | pull + start in one command, no credentials, status `200`, exact body |
| OPS-STORY-001-S2 | OPS-STORY-001 | Ch. 7.4; Ch. 7.6; ADR-009 | `latest` on `127.0.0.1:8000`, status `200`, exact body |
| OPS-INFRA-001.1-S1 | OPS-INFRA-001.1 → OPS-STORY-001 | Ch. 7.1–7.4; ADR-009 | pull shown in output, container ID printed, no build |
| OPS-INFRA-001.1-S2 | OPS-INFRA-001.1 → OPS-STORY-001 | RISK-03; Ch. 7.4 | no `Pulling` step after pre-pull, status `200`, exact body |
| OPS-INFRA-001.1-S3 | OPS-INFRA-001.1 → OPS-STORY-001 | Ch. 7.4 | unpublished tag: non-zero exit, no container, no build |
| NAV-INFRA-001.2-S4 | NAV-INFRA-001.2 → OPS-STORY-001 (reused) | Ch. 8.3; TC-6; QR-08; ADR-005 | one INFO log line with `blocked_count` `0` |

---

## OPS-STORY-002 — Distinguish validation and unhandled errors

**AS A** developer
**I WANT** `ValidationError` and unhandled exceptions to be logged distinctly and unhandled exceptions to return HTTP 500 with `{"error": "internal error"}`
**SO THAT** every failure is visible with `docker logs` and callers get the right body

**Architecture:** Error handling (Ch. 8.2) · Logging (Ch. 8.3) · HTTP mapping (Ch. 8.1) · FastAPI Route Adapter and Logger Adapter (Ch. 5.2) · QR-08, QR-09 (Ch. 10) · TC-6 · ADR-005 · ADR-009
**Priority:** 6 · Supporting
**Depends on:** NAV-STORY-001 (Route Adapter and Logger Adapter), INPUT-STORY-001 (ValidationError → HTTP 400 path), NAV-INFRA-001.1 / NAV-INFRA-001.2 (container and log channel)
**Implementation order:** reuse NAV-INFRA-001.1 / NAV-INFRA-001.2 with the added scenarios below → OPS-BE-002.1 → OPS-BE-002.2 → end-to-end scenarios below

### SCENARIO 1: A validation error returns 400 and one WARNING log entry

**Scenario ID**: OPS-STORY-002-S1

**GIVEN**
* The Rover Service is running in Docker

**WHEN**
* I send `POST /simulate` with `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "FFX"}` and read `docker logs`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value is a non-empty string containing `"X"`
* `docker logs` shows exactly one new JSON line for that request
* The line has `level` `"WARNING"` and `event` `"validation_error"`, with `result` `null` and `error` containing `"X"`

### SCENARIO 2: An unhandled exception returns 500 and one ERROR log entry

**Scenario ID**: OPS-STORY-002-S2

**GIVEN**
* The FastAPI application is started with `TestClient`
* The Command Executor is replaced by a stub that raises `RuntimeError("boom")`
* The Logger Adapter writes to a captured stdout stream (the same channel Docker logs)

**WHEN**
* I post `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "F"}` to `/simulate`

**THEN**
* The response status is `500`
* The response body is exactly `{"error": "internal error"}` and does not contain `"boom"`
* The captured stdout contains exactly one new JSON line with `level` `"ERROR"` and `event` `"unhandled_error"`
* The line contains the text `Traceback (most recent call last)` and `RuntimeError: boom`

### SCENARIO 3: The two error classes are distinguishable by level and event alone

**Scenario ID**: OPS-STORY-002-S3

**GIVEN**
* One validation-error request and one unhandled-exception request were processed as in S1 and S2
* Their two JSON log entries are available in one log stream

**WHEN**
* I compare only the `level` and `event` fields of the two entries

**THEN**
* The pairs are `("WARNING", "validation_error")` and `("ERROR", "unhandled_error")` in that order
* The two pairs are different, with no need to parse the message text (QR-09)

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

#### OPS-BE-002.1 — Route Adapter classifies errors at the HTTP boundary

**AS A** developer
**I WANT** the FastAPI Route Adapter to catch `ValidationError` as HTTP 400 and let unhandled exceptions become HTTP 500 with a fixed body
**SO THAT** internal exception detail never leaks to the caller

**Architecture:** FastAPI Route Adapter (Ch. 5.2) · Ch. 8.1–8.2 (error-handling pattern) · Ch. 8.2 (no internal detail) · ADR-007 · QR-09

##### SCENARIO 1: An unhandled exception becomes 500 with a fixed body

**Scenario ID**: OPS-BE-002.1-S1

**GIVEN**
* The FastAPI application is started with `TestClient`
* A stub replaces `Command Executor.execute` and raises `RuntimeError("boom")`

**WHEN**
* I post `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "F"}` to `/simulate`

**THEN**
* The response status is `500`
* The body is exactly `{"error": "internal error"}`
* The string `"boom"` does not appear in the response body

##### SCENARIO 2: A ValidationError stays 400 and does not use the 500 path

**Scenario ID**: OPS-BE-002.1-S2

**GIVEN**
* The FastAPI application is started with `TestClient`
* A spy records calls to `logger.warning` and `logger.exception`

**WHEN**
* I post `{"start": {"x": 0, "y": 0, "heading": "N"}, "grid": {"width": 3, "height": 3, "obstacles": []}, "commands": "FFX"}` to `/simulate`

**THEN**
* The response status is `400`
* The body has exactly one field `error`, whose value contains `"X"`
* `logger.warning` was called with event `"validation_error"` and `logger.exception` was not called

---

#### OPS-BE-002.2 — Logger Adapter emits distinct JSON error entries

**AS A** developer
**I WANT** the Logger Adapter to emit one JSON entry per error with `WARNING`/`validation_error` or `ERROR`/`unhandled_error`
**SO THAT** both failure classes are identifiable in `docker logs` without reading message text

**Architecture:** Logger Adapter (Ch. 5.2) · Ch. 8.2 (log calls) · Ch. 8.3 (format, mandatory fields, levels) · ADR-005 · QR-08, QR-09

##### SCENARIO 1: A validation warning contains the mandatory fields

**Scenario ID**: OPS-BE-002.2-S1

**GIVEN**
* The Logger Adapter is configured with a captured stdout stream
* A `ValidationError` with message `"unknown command X"` was raised for the request from OPS-STORY-002-S1

**WHEN**
* The Logger Adapter writes the validation-error entry

**THEN**
* The captured stream contains one JSON line with `level` `"WARNING"`, `event` `"validation_error"`, `error` `"unknown command X"` and `result` `null`
* The line contains the fields `request_id`, `grid`, `start`, `command_count` and `duration_ms`, with `command_count` `3`

##### SCENARIO 2: An unhandled error entry includes the traceback

**Scenario ID**: OPS-BE-002.2-S2

**GIVEN**
* The Logger Adapter is configured with a captured stdout stream
* `RuntimeError("boom")` was caught by the Route Adapter and logged with `exc_info=True`

**WHEN**
* The Logger Adapter writes the unhandled-exception entry

**THEN**
* The captured stream contains one JSON line with `level` `"ERROR"` and `event` `"unhandled_error"`
* The line contains all fields listed in Ch. 8.3, has `result` `null`, and includes `Traceback (most recent call last)` and `RuntimeError: boom`

##### SCENARIO 3: Level and event alone separate the two entries

**Scenario ID**: OPS-BE-002.2-S3

**GIVEN**
* The two JSON entries from OPS-BE-002.2-S1 and OPS-BE-002.2-S2 are in the captured stream

**WHEN**
* I read only the `level` and `event` fields of each entry

**THEN**
* The first entry yields `("WARNING", "validation_error")` and the second yields `("ERROR", "unhandled_error")`
* Neither pair occurs in the other entry

---

### Infrastructure sub-stories

Reused from NAV-STORY-001 and OPS-STORY-001 — no new deployment or log channel is introduced.

**Reused `NAV-INFRA-001.1` — Dockerfile + docker-compose.yml starting the Rover Service. Architecture: Ch. 7.1–7.3, TC-2, TC-3, ADR-009.**

##### ADDITIONAL SCENARIO S5: Error responses do not stop the container

**Scenario ID**: NAV-INFRA-001.1-S5

**GIVEN**
* The service was started with `docker compose up -d` and its container ID is recorded

**WHEN**
* I send the invalid request from OPS-STORY-002-S1, then the valid request from NAV-STORY-001-S1 to `http://127.0.0.1:8000/simulate`

**THEN**
* The first response status is `400` and the second is `200`
* The container ID is unchanged and the container is still running

**Reused `NAV-INFRA-001.2` — one structured JSON log entry per request. Architecture: Ch. 8.3, TC-6, QR-08, QR-09, ADR-005.**

##### ADDITIONAL SCENARIO S5: A rejected request emits no success entry

**Scenario ID**: NAV-INFRA-001.2-S5

**GIVEN**
* The Rover Service is running in Docker and the current `docker logs` line count is recorded

**WHEN**
* I send the invalid request from OPS-STORY-002-S1

**THEN**
* `docker logs` shows exactly one new JSON line for that request
* The line has `level` `"WARNING"` and `event` `"validation_error"`
* No new line with `level` `"INFO"` or `event` `"simulation_complete"` appears

##### ADDITIONAL SCENARIO S6: An ERROR entry reaches the captured stdout channel

**Scenario ID**: NAV-INFRA-001.2-S6

**GIVEN**
* The Logger Adapter writes to the stdout stream captured by Docker (TC-6)
* `RuntimeError("boom")` was logged by the Route Adapter with `exc_info=True`

**WHEN**
* The Logger Adapter emits the unhandled-error entry

**THEN**
* The stdout stream contains exactly one new JSON line with `level` `"ERROR"` and `event` `"unhandled_error"`
* The line includes `Traceback (most recent call last)`, so it is readable from `docker logs` in the running container

Not applicable - no simulation data store: errors are returned in the HTTP response and logged to stdout; nothing is persisted (ADR-001, TC-4, Ch. 4.1).
Not applicable - no events: error responses are synchronous HTTP responses; no message broker is used (ADR-007, Ch. 3.2).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| OPS-STORY-002-S1 | OPS-STORY-002 | Ch. 8.1–8.3; QR-09 | status `400`, one `error` field, one WARNING `validation_error` line |
| OPS-STORY-002-S2 | OPS-STORY-002 | Ch. 8.2; QR-09; ADR-005 | status `500`, body `{"error": "internal error"}`, one ERROR line with traceback |
| OPS-STORY-002-S3 | OPS-STORY-002 | QR-09; Ch. 8.3 | pairs `("WARNING","validation_error")`, `("ERROR","unhandled_error")` |
| OPS-BE-002.1-S1 | OPS-BE-002.1 → OPS-STORY-002 | Ch. 5.2 Route Adapter; Ch. 8.2 | status `500`, exact body, no `"boom"` in response |
| OPS-BE-002.1-S2 | OPS-BE-002.1 → OPS-STORY-002 | Ch. 8.1–8.2; ADR-007 | status `400`, `logger.warning` called, `logger.exception` not called |
| OPS-BE-002.2-S1 | OPS-BE-002.2 → OPS-STORY-002 | Ch. 8.3; ADR-005; QR-08 | one WARNING line with `error` and mandatory fields |
| OPS-BE-002.2-S2 | OPS-BE-002.2 → OPS-STORY-002 | Ch. 8.2–8.3; QR-09 | one ERROR line with traceback text |
| OPS-BE-002.2-S3 | OPS-BE-002.2 → OPS-STORY-002 | QR-09 Verification | two distinct level/event pairs |
| NAV-INFRA-001.1-S5 | NAV-INFRA-001.1 → OPS-STORY-002 (reused) | Ch. 7.1–7.3; ADR-009 | `400` then `200`, same container ID still running |
| NAV-INFRA-001.2-S5 | NAV-INFRA-001.2 → OPS-STORY-002 (reused) | Ch. 8.3; QR-08, QR-09; ADR-005 | one WARNING line, no INFO success line |
| NAV-INFRA-001.2-S6 | NAV-INFRA-001.2 → OPS-STORY-002 (reused) | Ch. 8.2–8.3; TC-6; ADR-005 | one ERROR line on stdout with traceback |

---

## OPS-STORY-004 — Keep the OpenAPI contract consistent with domain types

**AS A** Mission Operator
**I WANT** the generated OpenAPI contract to stay consistent with the domain types
**SO THAT** clients built from `/openapi.json` do not drift from the API

**Architecture:** CV-5 (JSON schema from route models) · ADR-007 (generated `/openapi.json`, no static spec) · RISK-02 (contract drift, CI contract test) · FastAPI Route Adapter and domain types (Ch. 5.2) · DEBT-02 · Ch. 7.5 (CI stages) · Glossary: OpenAPI, Simulation Request, Simulation Result (Ch. 12)
**Priority:** 7 · Supporting
**Depends on:** NAV-STORY-001 (Route Adapter, domain types, `/openapi.json`) and OPS-STORY-003 (CI pipeline that runs the contract check)
**Implementation order:** reuse OPS-INFRA-003.1 / OPS-INFRA-003.2 with the added scenarios below → OPS-BE-004.1 → end-to-end scenarios below

### SCENARIO 1: A client built from the contract can run a Simulation

**Scenario ID**: OPS-STORY-004-S1

**GIVEN**
* The Rover Service is running
* The OpenAPI document at `/openapi.json` is the only schema description available (no static spec file, ADR-007)

**WHEN**
* I request `GET /openapi.json`, resolve its `$ref` entries, and post the request from NAV-STORY-001-S1 using field names taken from that document

**THEN**
* The `GET` response status is `200`
* The document contains path `/simulate` with method `post`
* The request schema has exactly the fields `start`, `grid` and `commands`
* The HTTP 200 response schema has exactly the fields `position`, `heading` and `blocked`; each `blocked` item has exactly `index` and `reason`
* The `heading` field accepts exactly `N`, `S`, `E`, `W` and the `reason` field exactly `obstacle`, `boundary`
* The `POST /simulate` response status is `200` and its body is `{"position": {"x": 2, "y": 2}, "heading": "E", "blocked": []}`

### SCENARIO 2: A route-model divergence fails the build before publication

**Scenario ID**: OPS-STORY-004-S2

**GIVEN**
* PR commit `4d5e6f7` renames the route response model field `heading` to `direction` while `SimulationResult` still defines `heading` (RISK-02)

**WHEN**
* The GitHub Actions workflow runs the contract check comparing `/openapi.json` with schemas derived from the domain types

**THEN**
* The contract-check step exits with a non-zero status and its log names both `heading` and `direction`
* The job conclusion is `failure`
* No tag `ghcr.io/OWNER/rover-service:4d5e6f7` is pushed to GHCR
* `ghcr.io/OWNER/rover-service:latest` still resolves to the image built from commit `1a2b3c4`

### Frontend sub-stories

Not applicable - the system has no user interface (Ch. 3.4).

### Backend sub-stories

#### OPS-BE-004.1 — Route Adapter models mirror the domain types

**AS A** developer
**I WANT** a contract test that compares the FastAPI-generated schema with schemas derived from `SimulationRequest` and `SimulationResult`
**SO THAT** a hand-written mapping change cannot silently diverge (RISK-02)

**Architecture:** FastAPI Route Adapter (Ch. 5.2) · Domain types (Ch. 5.2, ADR-004) · RISK-02 · DEBT-02 · CV-5 · ADR-007

##### SCENARIO 1: The generated schemas match the domain types

**Scenario ID**: OPS-BE-004.1-S1

**GIVEN**
* The FastAPI application is started with FastAPI's `TestClient`

**WHEN**
* I resolve all `$ref` entries in `GET /openapi.json` and compare the request and HTTP 200 response schemas with schemas derived from `SimulationRequest` and `SimulationResult`

**THEN**
* The comparison passes with zero differing fields
* The request model fields are `start`, `grid`, `commands` and the response model fields are `position`, `heading`, `blocked`

##### SCENARIO 2: A renamed response field is detected

**Scenario ID**: OPS-BE-004.1-S2

**GIVEN**
* A test-only variant of the route adapter renames the response field `heading` to `direction` while `SimulationResult` keeps `heading`

**WHEN**
* The same contract comparison runs against that variant

**THEN**
* An `AssertionError` is raised
* Its message contains `heading` and `direction`
* The comparison does not pass

---

### Infrastructure sub-stories

Reused from OPS-STORY-003 — the existing GitHub Actions workflow gains one contract-check step (RISK-02 mitigation).

**Reused `OPS-INFRA-003.1` — GitHub Actions workflow that builds and publishes the image. Architecture: Ch. 7.5, OC-4, ADR-006; RISK-02 mitigation (CI contract test).**

##### ADDITIONAL SCENARIO S3: The CI contract check blocks publication on divergence

**Scenario ID**: OPS-INFRA-003.1-S3

**GIVEN**
* PR commit `4d5e6f7` contains the response-model divergence from OPS-STORY-004-S2

**WHEN**
* The PR workflow run finishes

**THEN**
* The run log shows a contract-check step that exits non-zero and names `heading` and `direction`
* The job conclusion is `failure`
* No `docker push` command runs and no `ghcr.io/OWNER/rover-service:4d5e6f7` tag appears in GHCR

**Reused `OPS-INFRA-003.2` — Pipeline failure visibility. Architecture: Ch. 7.5, QR-06 Verification, ADR-006; RISK-02.**

##### ADDITIONAL SCENARIO S3: The contract failure is visible in the run history

**Scenario ID**: OPS-INFRA-003.2-S3

**GIVEN**
* The workflow run for commit `4d5e6f7` failed at the contract-check step

**WHEN**
* I inspect the GitHub Actions run history for that commit

**THEN**
* The run history shows the failed step name `contract-check` with conclusion `failure`
* No stages 6–7 appear in the run log
* `ghcr.io/OWNER/rover-service:latest` still resolves to commit `1a2b3c4`

Not applicable - no simulation data store: the contract check compares generated schemas in memory; no simulation data or schema artefact is persisted (ADR-001, TC-4, Ch. 4.1; ADR-007 has no static spec file).
Not applicable - no events: contract checks run inside the synchronous CI workflow; the service interaction remains a synchronous `POST /simulate` HTTP request/response (ADR-007, Ch. 3.2).

### Traceability

| Scenario ID | Parent story | Architecture section | Testable assertion (THEN) |
|-------------|--------------|----------------------|---------------------------|
| OPS-STORY-004-S1 | OPS-STORY-004 | CV-5; ADR-007; Ch. 5.2 | `/simulate` `post`, exact schema fields, status `200`, exact body |
| OPS-STORY-004-S2 | OPS-STORY-004 | RISK-02; Ch. 7.5; ADR-006 | contract step fails, job `failure`, no tag, `latest` unchanged |
| OPS-BE-004.1-S1 | OPS-BE-004.1 → OPS-STORY-004 | ADR-007; CV-5; RISK-02 | zero differing fields, exact model field names |
| OPS-BE-004.1-S2 | OPS-BE-004.1 → OPS-STORY-004 | RISK-02; DEBT-02 | `AssertionError` naming `heading` and `direction` |
| OPS-INFRA-003.1-S3 | OPS-INFRA-003.1 → OPS-STORY-004 (reused) | Ch. 7.5; RISK-02; ADR-006 | contract step non-zero, job `failure`, no push or tag |
| OPS-INFRA-003.2-S3 | OPS-INFRA-003.2 → OPS-STORY-004 (reused) | QR-06 Verification; RISK-02 | run history shows failed `contract-check`, stages 6–7 absent |
