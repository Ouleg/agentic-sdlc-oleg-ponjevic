# 1. Introduction and Goals

## 1.1 Purpose

The **Mars Rover Simulator** executes a sequence of movement commands for a rover
on a rectangular grid. It accepts the rover's start position and heading, a grid
map that may contain obstacles, and a list of commands. It returns the rover's final
position and heading, and reports if any command was blocked by an obstacle or a
grid boundary.

The system is built as a learning kata (see
[codingdojo.org/kata/mars-rover](https://codingdojo.org/kata/mars-rover/)) and
serves as the target for a full TDD/BDD and CI/CD demonstration. It is delivered
as a Python 3.12 FastAPI application served by Uvicorn inside a Docker container;
no cloud account is required. Only the HTTP and logging adapters depend on this
runtime — the pure domain core is unchanged.

## 1.2 Functional Requirements

| ID   | Requirement |
|------|-------------|
| FR-1 | Accept a start position `(x, y)` and an initial heading `N`, `S`, `E`, or `W`. |
| FR-2 | Accept a rectangular grid with zero or more obstacle positions. |
| FR-3 | Accept a command string consisting of `F` (forward), `L` (turn left 90°), and `R` (turn right 90°). |
| FR-4 | Execute the commands in order and track the rover's position and heading after each step. |
| FR-5 | When an `F` command would leave the grid or land on an obstacle, skip that command (rover keeps its current position and heading), record the blocked command and its zero-based index in the command list, and continue executing the remaining commands. |
| FR-6 | Return the final `(x, y)` position, heading, and the list of blocked commands (each with its index and reason: `obstacle` or `boundary`). |
| FR-7 | Reject invalid input — unknown command characters, a start position outside the grid or on an obstacle, or an empty grid — with a clear validation error; no simulation is run. |

## 1.3 Quality Goals

The following quality goals are ordered by priority. They drive the architecture
decisions in Chapter 4 and the quality requirements in Chapter 10.

| Priority | Quality Goal | Scenario |
|----------|-------------|---------|
| 1 | **Correctness** | Every FR-4 through FR-7 scenario is verified by a BDD test that runs in CI. No simulation produces a wrong position or silently ignores an obstacle. The same input always produces the same output (deterministic). |
| 2 | **Testability** | The domain core can be exercised by pytest/pytest-bdd directly, without Docker, a network, or mocks of external services. |
| 3 | **Deployability** | A single `docker run` (or `docker compose up`) starts the service locally; CI/CD builds the image, publishes it to GitHub Container Registry (GHCR), and runs without manual steps. |
| 4 | **Simplicity** | No component, storage layer, or integration is added until a requirement demands it. |
| 5 | **Observability** | Every request emits a structured JSON log entry to stdout (read with `docker logs`) that includes the input, the outcome, and any blocking event. |

## 1.4 Stakeholders

| Stakeholder | Role | Key concern |
|-------------|------|-------------|
| Mission Operator | Submits simulation requests via the HTTP API | Correct results, clear error messages |
| Developer / Kata learner | Writes and maintains the code | Clean domain model, easy to test locally |
| CI/CD pipeline | Builds, tests and publishes the container image automatically | Reproducible build, fast feedback loop |
| Docker runtime & GHCR (implicit) | Runs the container and stores published images | Minimal, reproducible image; no cloud account or IAM configuration |
| Course instructor / reviewer | Reviews the architecture and PRs | Completeness and consistency of arc42 and C4 |
