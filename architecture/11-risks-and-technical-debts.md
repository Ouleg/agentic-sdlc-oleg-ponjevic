# 11. Risks and Technical Debts

Risks are potential future problems that may materialise. Technical debts are known
shortcomings accepted deliberately in the MVP. Each item has a priority
(High / Medium / Low) based on likelihood × impact and a mitigation or resolution path.

## 11.1 Risks

### RISK-01 — Unauthenticated API endpoint

| | |
|---|---|
| **Priority** | High |
| **Description** | The `POST /simulate` endpoint is available on the container's listening port (default 8000) with no authentication or authorisation. Any client that can reach the host or container can call it. |
| **Impact** | There is no cloud bill to inflate, but an unrestricted caller can consume the host's CPU and memory, send large payloads, or probe for vulnerabilities. If the container port is published beyond localhost, the blast radius grows. |
| **Likelihood** | Medium — the port is open by design for local use; an exposed host or a shared network makes discovery trivial. |
| **Mitigation** | The MVP mitigations are only (a) bind the container port to localhost by default in `docker-compose.yml` and (b) an explicit request body-size cap in the FastAPI Route Adapter. Authentication and request rate limiting are explicitly deferred and tracked in DEBT-04; no cloud API gateway, IAM, or Cognito is involved. |

---

### RISK-02 — OpenAPI contract drift from domain types

| | |
|---|---|
| **Priority** | Medium |
| **Description** | FastAPI generates the OpenAPI spec from the route adapter's request/response models (ADR-007), so the spec and those models cannot drift silently. The mapping between those models and the domain types (`SimulationRequest`, `SimulationResult`) is still hand-written and can diverge. |
| **Impact** | The FastAPI Route Adapter may accept or return shapes that differ from what the generated spec documents, breaking operator clients and failing the reviewer's contract check. |
| **Likelihood** | Medium — without automated enforcement, mapping drift is a common occurrence in iterative development. |
| **Mitigation** | Keep one source of truth: derive the route models from the domain types, or add a CI contract test that compares the generated `/openapi.json` against schemas produced from the domain types and fails the build on divergence. Until that step exists, treat route-model changes as requiring a paired domain-type change in the same PR. |

---

### RISK-03 — Container startup and image pull latency

| | |
|---|---|
| **Priority** | Low |
| **Description** | On a fresh `docker run` or `docker compose up`, Docker may need to pull the published image and the Python application must import FastAPI and Uvicorn before the first request can be served (typically a few hundred milliseconds to seconds on a first pull). |
| **Impact** | The first request after starting the container responds more slowly than subsequent ones. For a kata this is acceptable; for a production SLA it may not be. |
| **Likelihood** | High on a new machine or after an image update; low on a warm local image cache. |
| **Mitigation** | Acceptable for the MVP under ADR-009. Pre-pull the published tag with `docker pull` and keep the container running to avoid repeat startup. If a latency SLA is introduced, evaluate a different deployment model and record it as a new ADR. |

---

### RISK-04 — Large grid or long command list exhausts container resources

| | |
|---|---|
| **Priority** | Low |
| **Description** | FastAPI and Uvicorn do not impose a small default request-body limit. A grid with millions of obstacle coordinates or a command string of extreme length could consume significant memory and CPU inside the single container. |
| **Impact** | Very large requests could exhaust container memory (OOM kill) or stall the event loop; no gateway returns an early HTTP 413, so the caller may get an unclear error. |
| **Likelihood** | Low — the kata specifies a rectangular grid with a modest number of obstacles; no realistic input approaches these limits. |
| **Mitigation** | Document effective input-size limits via the generated OpenAPI spec and add an explicit body-size cap and validation in the FastAPI Route Adapter (or a reverse proxy). If large grids become a requirement, evaluate streaming or chunked processing and record it as a new ADR. |

---

### RISK-05 — CI/CD token and workflow supply-chain exposure

| | |
|---|---|
| **Priority** | Medium |
| **Description** | The GitHub Actions workflow uses the automatic `GITHUB_TOKEN` with `packages: write` to push images to GHCR. If the workflow is modified through a compromised dependency or an unreviewed change, or the token is over-scoped, an attacker could publish a malicious image under the repository's name. |
| **Impact** | Unauthorised image publication and supply-chain compromise for anyone who pulls and runs the affected tag. |
| **Likelihood** | Low with correct configuration; medium if fork PRs can change the workflow or if permissions are broader than needed. |
| **Mitigation** | Scope the token to the minimum `packages: write` permission, pin action versions to commit SHAs, require PR review for workflow changes, and never print tokens in logs (TC-8). There are no cloud credentials, IAM roles, or OIDC providers to manage. |

---

## 11.2 Technical Debts

### DEBT-01 — No simulation history or replay

| | |
|---|---|
| **Priority** | Low |
| **Description** | Every request is stateless; completed simulations are not stored. There is no way to retrieve or replay a past result. |
| **Accepted because** | The kata requires no persistence and ADR-001 explicitly defers storage. Adding a database or object store would increase complexity without a current requirement. |
| **Resolution path** | Add a storage port (e.g. `SimulationRepository` protocol) and a database adapter when a replay or history requirement is confirmed. The hexagonal structure makes this addition contained to a new adapter and a new port; the domain core does not change. |

---

### DEBT-02 — Manual validation without full schema generation

| | |
|---|---|
| **Priority** | Low |
| **Description** | The domain `Validator` is hand-coded rather than generated from a schema. As accepted in ADR-003, this is intentional for the MVP. FastAPI's Pydantic models handle HTTP-level shape checks, but the four domain validation rules and the route models must be kept in sync manually. |
| **Accepted because** | Four stable rules do not justify a schema-code generation dependency (ADR-003). |
| **Resolution path** | If the input model grows beyond four checks, evaluate generating more of the validation and schema from a shared definition while keeping the domain `Validator` for business-rule checks. |

---

### DEBT-03 — No distributed tracing

| | |
|---|---|
| **Priority** | Low |
| **Description** | The system emits structured JSON logs with a per-request UUID4 correlation ID (Chapter 8.3) but has no distributed tracing or log aggregation. Cross-request debugging relies on `docker logs` and manual correlation. |
| **Accepted because** | A single-container, single-request system has no cross-service hops to trace; adding tracing or metrics dependencies was ruled out by YAGNI in ADR-005. |
| **Resolution path** | Add an OpenTelemetry tracer and a Docker log driver that forwards to a local collector if the system grows to multiple containers or external service calls. |

---

### DEBT-04 — No authentication and no request rate limiting / Uvicorn concurrency cap

| | |
|---|---|
| **Priority** | Low |
| **Description** | The service has no authentication, no request rate limiting and no concurrency cap; Uvicorn serves requests with only its default worker and event-loop settings. These controls are the part of the RISK-01 mitigation explicitly deferred in the MVP, which only binds the published port to localhost and caps request body size in the FastAPI Route Adapter. A client that can reach the port can still flood the container. |
| **Accepted because** | For a local kata with one operator, localhost binding plus the body-size cap are sufficient; the authentication mechanism and the right limit values cannot be determined before real traffic exists. |
| **Resolution path** | Add authentication in the FastAPI Route Adapter (e.g. an API-key header or bearer-token check), rate limiting in the adapter or a reverse proxy, and tune Uvicorn worker/concurrency settings once usage patterns are known; record the chosen mechanism as a new ADR and remove this debt entry, closing the deferred part of RISK-01. |
