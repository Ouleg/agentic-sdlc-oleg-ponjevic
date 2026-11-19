# 2. Architecture Constraints

## 2.1 Technical Constraints

| ID   | Constraint | Reason |
|------|-----------|--------|
| TC-1 | Implementation language is **Python 3.12**. | Project standard; existing tooling (pyproject.toml, black, ruff, bandit) targets this version. |
| TC-2 | Runtime is a Python 3.12 **FastAPI** application served by **Uvicorn** in a **Docker** container, exposing the same `POST /simulate` JSON API. | Self-contained, cloud-free runtime; runs identically with `docker run` or `docker compose`, with no account or infrastructure to provision. |
| TC-3 | The runtime is defined by a **Dockerfile** and a **docker-compose.yml**; CI/CD builds the image and publishes it to **GitHub Container Registry (GHCR)**. | These files are the single source of truth for the runtime environment; no cloud infrastructure-as-code tool or cloud account is required. |
| TC-4 | The system is **stateless**: no database or persistent storage for the MVP. | Every request carries its full input; ADR-001 rules out storage until a requirement demands it. |
| TC-5 | Tests use **pytest** for unit tests and **pytest-bdd** for behaviour scenarios. | Mandated by the kata and CI/CD module; BDD feature files are the executable specification. |
| TC-6 | Structured JSON logs are written to **stdout** by the Logger Adapter and read with `docker logs`. | Standard container log channel; no log shipping or aggregation service is introduced. |
| TC-7 | The domain core must have **no framework, SDK, or I/O dependencies**. | Hexagonal architecture principle; the core must be runnable and testable without Docker, a web framework, or any infrastructure. |
| TC-8 | Secrets and configuration are passed via **environment variables** or Docker Compose configuration; none are hard-coded in source. | Security baseline; enforced by bandit and code review; no secret store is introduced in the MVP. |

## 2.2 Organisational Constraints

| ID   | Constraint | Reason |
|------|-----------|--------|
| OC-1 | Architecture is documented using the **arc42 template** with **C4 model** diagrams. | Required by the course; the instructor reviews chapters and diagrams for completeness and consistency. |
| OC-2 | All diagrams are written in **PlantUML** and stored under `architecture/diagrams/`. | Enables version control and automated SVG generation in CI. |
| OC-3 | Every significant architectural decision is recorded as an **ADR** in `architecture/09-architecture-decisions.md`. | Provides a traceable decision log for the reviewer and future maintainers. |
| OC-4 | The CI/CD pipeline must be able to **build, test, and publish the container image to GHCR without manual intervention**. | A core learning objective of the CI/CD module. |
| OC-5 | The repository follows the **branch-and-PR workflow**; no direct commits to the main branch. | Required by the course; the reviewer approves PRs. |

## 2.3 Conventions

| ID   | Constraint | Reason |
|------|-----------|--------|
| CV-1 | The **pre-commit toolchain** runs on every `git commit`: **black** (formatting), **isort** (import ordering), **ruff** (linting), **bandit** (security scanning), **detect-secrets** (credential leak detection), and a **PlantUML hook** that regenerates and stages the SVG for every modified `.puml` file. | Keeps code quality, security, and diagram artefacts consistent without relying on developer discipline alone. |
| CV-2 | **Commit messages** follow the format `#<issue> <type>(<scope>): <description>` (e.g. `#42 feat(domain): add obstacle detection`), enforced by a **commit-msg hook**. Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `perf`, `style`. | Links every commit to a tracked issue and provides a machine-readable changelog; rejected automatically if the format is wrong. |
| CV-3 | **Branch names** follow `<prefix>/<short-kebab-description>` with no issue number in the branch name (e.g. `feature/obstacle-detection`, `fix/boundary-wrap`, `docs/arc42-chapter-3`). Allowed prefixes: `feature/`, `fix/`, `docs/`, `chore/`. | Keeps branch lists scannable and separates concern type from the work description. |
| CV-4 | The ubiquitous language defined in Chapter 12 (Glossary) is used consistently in code, tests, diagrams, and documentation. | Prevents terminology drift between the domain model and the documentation. |
| CV-5 | API request and response bodies use **JSON**; the schema is defined in the OpenAPI specification that FastAPI generates from the route adapter's request/response models. | Provides a contract between the operator client and the FastAPI route adapter that the reviewer can validate. |
