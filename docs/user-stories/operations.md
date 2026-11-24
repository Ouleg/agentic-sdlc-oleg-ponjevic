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
