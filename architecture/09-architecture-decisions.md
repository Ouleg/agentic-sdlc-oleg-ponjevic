# 9. Architecture Decisions

## ADR-001: Python 3.12 Serverless API on AWS Lambda, Stateless Simulation

**Status:** Accepted

**Context:**
The Mars Rover Simulator receives a start position and direction, a grid map with
obstacles and a sequence of commands, and returns the final position and direction
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
