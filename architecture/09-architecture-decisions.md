# 9. Architecture Decisions

## ADR-001: Python 3.12 Serverless API on AWS Lambda, Stateless Simulation

**Status:** Accepted - runtime part (AWS Lambda, API Gateway, SAM) superseded by ADR-009

**Context:**
The Mars Rover Simulator receives a start position and heading, a grid with
obstacles and a sequence of commands, and returns the final position and heading
of the rover. The system must be easy to test (TDD/BDD in later modules), cheap to
run, and deployable through a CI/CD pipeline with AWS SAM.

**Decision:**
- **Language:** Python 3.12.
- **Architecture style:** Hexagonal (ports and adapters). The domain core
  (command parsing, navigation, obstacle detection) is pure Python with no
  framework or cloud dependencies.
- **Runtime / framework:** AWS Lambda behind Amazon API Gateway (HTTP API),
  defined and deployed with AWS SAM. A thin Lambda handler adapts JSON requests
  to the domain core.
- **Data storage:** None for the MVP. Every request carries the full input
  (map, start position, commands), so the simulation is stateless.
- **Testing:** pytest for unit tests, pytest-bdd for behaviour scenarios.

**Rationale:**
- Python is already the project standard (pyproject.toml, black, ruff, bandit).
- A pure domain core can be fully tested without AWS, which fits TDD/BDD.
- Lambda scales to zero and costs nothing when idle; SAM gives infrastructure
  as code that the CI/CD module can deploy automatically.
- A stateless design avoids a database, connection handling and data migration
  for a problem that does not need persistence.

**Consequences:**
- Simulation history is not stored; if replay or mission history is needed later,
  a storage adapter (e.g. DynamoDB) must be added behind a new port.
- Large maps are limited by API Gateway / Lambda payload size limits.
- Cold starts add latency to the first request, which is acceptable for this use case.
- The team must keep AWS-specific code inside adapters so the core stays portable.

## ADR-002: Navigator Handles All Three Commands (F, L, R)

**Status:** Accepted

**Context:**
The domain core needs a component that translates commands into rover state changes.
The initial design split the responsibility: the Command Executor handled L and R
turns directly and only delegated F to the Navigator. This meant heading arithmetic
lived in two places and the Navigator could not be tested for the full command set
in isolation.

**Decision:**
The Navigator handles all three command types through a single `apply(command,
position, heading, grid)` entry point. For F it computes the candidate next
position and checks obstacles and boundaries, returning either a new `Position` or
a `BlockedMove`. For L and R it computes and returns the new `Heading`. The Command
Executor only iterates the list, calls `Navigator.apply` for every command, and
records `BlockedMove` entries.

**Rationale:**
- All rover state-change logic lives in one component, making the Navigator the
  single source of truth for movement and turning rules.
- The Executor becomes a pure iteration loop with no physics knowledge, reducing
  its test surface to sequencing and result accumulation.
- `Navigator` can be unit-tested for all three command types without involving the
  Executor.

**Consequences:**
- The Navigator's `apply` return type is a union: `Position | Heading | BlockedMove`;
  the Executor must dispatch on the returned type.
- Turning can never produce a `BlockedMove` (L/R always succeed), so the type
  distinction is clear and exhaustive.

---

## ADR-003: Manual Validation Over a Schema Library

**Status:** Accepted

**Context:**
The `Validator` component must enforce FR-7: reject empty grids, out-of-bounds or
obstacle-coincident start positions, and unknown command characters. Python
ecosystem options include Pydantic, marshmallow, and jsonschema for declarative
validation.

**Decision:**
Validation is implemented as explicit Python code in `rover/domain/validator.py`
using plain `if` statements and raising `ValidationError`. No third-party
validation library is added.

**Rationale:**
- The validation rules are few (four checks) and stable; a schema library adds a
  dependency without reducing the code volume meaningfully.
- Keeping validation in the domain core as plain Python preserves TC-7 (no
  framework dependencies in the core) and keeps the `ValidationError` type fully
  owned by the domain.
- The rules are expressed in the kata specification in prose, not as a JSON schema;
  translating them to code directly is clearer than encoding them in a schema DSL.
- If the input schema grows significantly (e.g. multiple rovers, waypoints), Pydantic
  can be introduced as an adapter-layer concern without touching the domain core.

**Consequences:**
- Each new validation rule requires a test case and a code change; there is no
  automatic schema-driven validation.
- Pydantic or similar must be evaluated and added as an ADR if the input model
  grows beyond the current four checks.

---

## ADR-004: Python Dataclasses as the Domain Model

**Status:** Accepted

**Context:**
The domain core needs immutable, typed value objects (`Position`, `Heading`,
`Command`, `Grid`, `SimulationRequest`, `BlockedMove`, `SimulationResult`) that
carry no framework or persistence dependencies.

**Decision:**
All domain types are implemented as Python `dataclasses` (with `frozen=True` for
value objects) and `enum.Enum` for `Heading` and `Command`. No ORM, Pydantic
model, or attrs class is used in the domain layer.

**Rationale:**
- `dataclasses` and `enum` are part of the Python standard library; they add no
  dependencies and satisfy TC-7.
- `frozen=True` enforces immutability, which supports the determinism quality goal:
  a frozen dataclass cannot be accidentally mutated during a simulation run.
- `enum.Enum` for `Heading` and `Command` makes exhaustiveness checking in `match`
  statements possible and prevents invalid values from being constructed.
- Pydantic models would couple the domain types to Pydantic's validation lifecycle,
  which belongs in the adapter layer, not the core.

**Consequences:**
- Serialisation to/from JSON must be handled in the FastAPI Route Adapter, not in
  the domain types themselves.
- If the domain model needs schema evolution (versioning), a separate serialisation
  layer must be introduced in the adapter.

---

## ADR-005: Structured JSON Logging via stdout

**Status:** Accepted

**Context:**
The system must emit structured JSON logs to stdout for every request (quality
goal 5, TC-6), readable with `docker logs`. Options considered: `python-json-logger`,
plain Python `logging` with a custom formatter, and `print()` statements.

**Decision:**
The Logger Adapter wraps Python's standard `logging` module with a custom
`logging.Formatter` subclass that serialises the log record to a single-line JSON
string on stdout. Docker captures stdout and `docker logs` reads it; no third-party
logging library or log shipper is added.

**Rationale:**
- Container stdout is the standard Docker log channel; no SDK call or cloud service
  is needed (TC-6).
- A custom JSON formatter over the standard library adds zero runtime dependencies
  and satisfies TC-7 for the adapter layer.
- A cloud-specific structured logger would pull in tracing, metrics and event
  parsing utilities that are not needed for this kata and would require a cloud
  provider; YAGNI (quality goal 4) rules it out for the MVP.
- `python-json-logger` is a reasonable alternative but is an additional dependency
  for functionality achievable in ~20 lines of standard-library code.

**Consequences:**
- The JSON log format is defined and maintained in this project; it must be kept
  consistent with the field definitions in Chapter 8.3.
- If tracing or metrics are added later, the logger can be replaced without
  touching the domain core.

---

## ADR-006: GitHub Actions CI/CD Publishing the Image to GHCR

**Status:** Accepted

**Context:**
The system requires a CI/CD pipeline that builds, tests, and publishes the service
automatically (OC-4). There is no cloud provider or deployment target: the
deployable artefact is a container image that anyone can pull and run locally. The
source repository is on GitHub and GitHub Container Registry is available to it.

**Decision:**
The CI/CD pipeline is implemented as a GitHub Actions workflow. On every pull
request it runs lint/security checks, all tests and a Docker build check. On every
merge to `main`, after those checks pass, it builds the image from the `Dockerfile`
and pushes it to GHCR, tagged with the commit SHA and `latest`. There is no
`sam build` or `sam deploy`, no AWS credentials, and no Prod approval stage on AWS;
publishing an image tag is the release action.

**Rationale:**
- GitHub Actions is co-located with the source repository; no separate CI server
  is needed.
- The feature-branch → PR → `main` workflow (OC-5) means `main` is always
  reviewed code; publishing a tag from it is safe.
- GHCR is the single artefact store; the automatic `GITHUB_TOKEN` with
  `packages: write` is scoped to the repository, so no long-lived cloud credentials
  are needed (TC-8).
- Anyone with Docker can pull and run the published image locally; there is no
  cloud environment to provision or approve.

**Consequences:**
- There is no cloud environment and no manual production approval gate; releasing
  means pushing a tag, which happens automatically on merge to `main`.
- The GitHub Actions YAML workflow file is the authoritative definition of the
  pipeline; changes to it must go through a PR like any other source change.
- If the project moves to a different SCM (e.g. GitLab), the pipeline definition
  must be rewritten; the Dockerfile and application code are unaffected.

## ADR-007: Single POST /simulate Endpoint with JSON and an OpenAPI Contract

**Status:** Accepted

**Context:**
The system exposes one operation: run a simulation and return the result. API design
options included REST-style resource endpoints (e.g. `POST /rovers`, `GET /rovers/{id}/result`),
a single RPC-style endpoint, and GraphQL. The request/response schema needs a formal
contract so the operator client and the FastAPI Route Adapter stay in sync and the
reviewer can validate the API independently of the code.

**Decision:**
The API exposes a single endpoint `POST /simulate` that accepts the full simulation
input in the JSON request body and returns the result in the JSON response body.
The request and response models are declared in the FastAPI Route Adapter. FastAPI
generates the OpenAPI 3.x specification from those models and serves it at
`/openapi.json`; there is no separate static spec file or API Gateway configuration.

**Rationale:**
- A single stateless operation maps naturally to one endpoint; there is no resource
  to create, retrieve, or delete (TC-4 — no persistence).
- `POST` is appropriate because the request body carries all input and the operation
  is not idempotent in the HTTP caching sense (though it is deterministic).
- An OpenAPI contract makes the schema machine-readable, enables client generation,
  and gives the course reviewer a precise artefact to inspect (CV-5, OC-1). Because
  FastAPI generates it from the same models used for request/response handling, the
  contract cannot drift from the code.
- REST resource endpoints and GraphQL both require state or a richer query model
  that this kata does not have; they add complexity without benefit (quality goal 4).

**Consequences:**
- Basic HTTP concerns (JSON content type and body shape) are handled by FastAPI's
  request models; domain validation is handled by the `Validator` component.
- If a second operation is added (e.g. `POST /validate`), it gets its own route
  and appears in the same generated OpenAPI spec rather than overloading `/simulate`.
- The generated spec stays in sync with the route adapter's models automatically;
  if manual serialisation is introduced later, keep it aligned with the
  `SimulationRequest` and `SimulationResult` domain types.

---

## ADR-008: A Blocked F Command Is Skipped and Reported; Response Is HTTP 200

**Status:** Accepted

**Context:**
When an `F` command would move the rover onto an obstacle or outside the grid, the
system must decide: halt the simulation and return an error, halt the simulation
and return a partial result, or skip the blocked command and continue.
The kata specification states the rover "does not move" and the stop "is reported";
it does not say simulation should halt. The choice of HTTP status code for a
response that contains blocked commands also requires a decision.

**Decision:**
When an `F` command is blocked, the rover keeps its current position and heading,
the blocked command is recorded with its zero-based index and reason (`obstacle` or
`boundary`), and execution continues with the next command (FR-5). The final
response always uses HTTP 200. The `blocked` field in the response body is an
empty list when no commands were blocked and a non-empty list otherwise (FR-6).

**Rationale:**
- Continuing after a block matches the kata description: the rover reports the
  obstacle and carries on; it does not abort the mission.
- A single simulation run may encounter multiple obstacles; halting on the first
  block would hide subsequent ones from the caller.
- HTTP 200 is correct because the simulation completed successfully; the blocked
  commands are a valid, expected outcome, not a server or client error. Using 4xx
  for a blocked move would misrepresent the semantics of HTTP status codes.
- Recording the zero-based index allows the caller to map each blocked command back
  to the original command string precisely.

**Consequences:**
- Callers must inspect the `blocked` field to determine whether all commands
  executed; an empty `blocked` list means a fully unobstructed run.
- The `Validator` still returns HTTP 400 for structurally invalid input (FR-7);
  HTTP 200 with a non-empty `blocked` list is not a substitute for validation
  errors.
- If a future requirement demands halting on the first block, this decision must
  be superseded by a new ADR and FR-5 updated accordingly.

---

## ADR-009: Run as a containerised FastAPI service, no cloud provider

**Status:** Accepted

**Context:**
ADR-001 originally placed the service on AWS Lambda behind API Gateway, defined
and deployed with SAM. The course for this kata does not provide an AWS account,
so the runtime must be something every participant can run and publish without
cloud credentials or infrastructure provisioning. The functional requirements and
the pure domain core are unchanged; only the runtime and delivery adapters need a
new decision.

**Decision:**
- **Runtime:** Python 3.12 FastAPI application served by Uvicorn inside a Docker
  container, exposing the same `POST /simulate` JSON API.
- **Packaging and local run:** `Dockerfile` and `docker-compose.yml`; start with
  `docker run` or `docker compose up`.
- **Logging:** structured JSON to stdout, read with `docker logs` (ADR-005).
- **CI/CD:** GitHub Actions runs the checks and tests, builds the image and
  publishes it to GHCR (ADR-006).
- **Domain core:** unchanged. `Validator`, `Command Executor`, `Navigator` and the
  domain types stay pure; the Lambda Handler is replaced by a FastAPI Route Adapter
  and the Logger Adapter is retained.
- **No cloud resources:** no IAM roles, CloudFormation/SAM stacks, API Gateway,
  CloudWatch, or Dev/Prod cloud environments.

**Alternatives considered:**
- **AWS Lambda + API Gateway with SAM (the ADR-001 runtime):** rejected — requires
  an AWS account, IAM and deployment permissions that the course does not provide.
- **SAM local with Docker:** rejected — still ties the project to SAM templates and
  AWS semantics while requiring AWS tooling; a plain container gives the same local
  execution without a cloud-shaped build.
- **Plain CLI application:** rejected — the kata requires an HTTP JSON API
  (ADR-007); a CLI would change the contract and the Mission Operator interaction.

**Rationale:**
- A container runs identically on any machine with Docker; no account, region or
  permissions need to be configured.
- FastAPI generates the OpenAPI contract from the route adapter's models (ADR-007)
  and keeps the JSON API unchanged.
- Publishing an image to GHCR gives a reproducible, traceable artefact that anyone
  can pull and run.
- The hexagonal boundary keeps HTTP and infrastructure concerns in adapters, so
  this change does not touch the domain core.

**Consequences:**
- ADR-001 remains accepted for language, hexagonal style, statelessness and
  testing; its runtime part (AWS Lambda, API Gateway, SAM) is superseded by this ADR.
- There is no elastic scaling, managed TLS or cloud log retention; local HTTP
  (port 8000) and `docker logs` replace them. A future cloud deployment requires a
  new ADR.
- Container images must be rebuilt and republished for each change; the GHCR tag
  is the release identifier.
- Chapters 2–8, 10 and 11 use container terminology and the diagrams are re-rendered;
  domain tests are unaffected.
