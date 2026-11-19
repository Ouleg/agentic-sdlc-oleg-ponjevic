# 12. Glossary

This glossary defines the ubiquitous language of the Mars Rover Simulator. Every
term listed here is used with exactly this meaning in code, tests, diagrams, and
documentation (CV-4). Where a term has a common general meaning that differs from
its domain meaning, the domain meaning takes precedence.

## Domain Terms

| Term | Definition |
|------|-----------|
| **Blocked Move** | The outcome when an `F` command cannot be executed because the target cell is an obstacle or lies outside the grid. The rover keeps its current position and heading; the blocked move is recorded with its zero-based index and reason. See FR-5. |
| **Boundary** | The edge of the grid. A move is blocked with reason `boundary` when the target cell's coordinates fall outside `[0, width-1] × [0, height-1]`. |
| **Command** | A single instruction in the command string: `F` (move forward one cell), `L` (turn left 90°), or `R` (turn right 90°). |
| **Command List** | The ordered sequence of `Command` values derived from the command string. The zero-based position of a command in this list is its index. |
| **Command String** | The raw string of command characters supplied by the Mission Operator (e.g. `"FFRFLF"`). The FastAPI Route Adapter parses it into a Command List before passing it to the domain core. |
| **Grid** | The rectangular terrain on which the rover moves, defined by a width, a height, and a set of obstacle positions. Coordinates are zero-based: `(0, 0)` is the bottom-left cell, `(width-1, height-1)` is the top-right cell. |
| **Heading** | The compass direction the rover is facing: `N` (north), `S` (south), `E` (east), or `W` (west). North is in the direction of increasing `y`; east is in the direction of increasing `x`. |
| **Index** | The zero-based position of a command in the Command List. Used in `BlockedMove` to identify which command was skipped. |
| **Mission Operator** | The human or automated client that submits simulation requests to the Rover Service over HTTP and receives results. |
| **Obstacle** | A cell in the grid that the rover cannot enter. Defined by its `(x, y)` coordinates. A move targeting an obstacle cell is blocked with reason `obstacle`. |
| **Position** | A cell in the grid identified by integer coordinates `(x, y)`. |
| **Reason** | The cause of a Blocked Move: `obstacle` if the target cell contains an obstacle, `boundary` if the target cell is outside the grid. |
| **Simulation** | A single execution of a command list starting from a given position and heading on a given grid, producing a final position, heading, and list of blocked moves. |
| **Simulation Request** | The validated, fully-typed input to the domain core: start `Position`, initial `Heading`, `Grid`, and `Command List`. Produced by the FastAPI Route Adapter after deserialisation and validation. |
| **Simulation Result** | The output of the domain core: final `Position`, final `Heading`, and the list of `BlockedMove` entries (empty if no commands were blocked). Serialised to the HTTP response by the FastAPI Route Adapter. |
| **Start Position** | The `(x, y)` coordinates of the rover at the beginning of a simulation. Must be inside the grid and not coincide with an obstacle (FR-7). |
| **Turn Left** | Rotate the rover's heading 90° anticlockwise: N → W → S → E → N. |
| **Turn Right** | Rotate the rover's heading 90° clockwise: N → E → S → W → N. |
| **Validation Error** | An exception raised by the `Validator` when the input violates FR-7. The FastAPI Route Adapter maps it to an HTTP 400 response; no simulation is run. |

## Technical and Infrastructure Terms

| Term | Definition |
|------|-----------|
| **Adapter** | A component in the outer ring of the hexagonal architecture that translates between the domain core and an external system (HTTP, logging). In this system: FastAPI Route Adapter, Logger Adapter. |
| **BDD (Behaviour-Driven Development)** | A testing approach in which scenarios are written in Gherkin (`Given / When / Then`) and executed by `pytest-bdd`. BDD feature files are the primary executable specification for FR-4 through FR-7. |
| **Command Executor** | The domain component that iterates the command list, calls the Navigator for every command, and accumulates `BlockedMove` entries. Returns the `SimulationResult`. |
| **Container Logs (stdout)** | The structured JSON log entries written to stdout by the Logger Adapter. Docker captures them and `docker logs` reads them; they are an external system in the C4 diagrams. |
| **Docker** | The container runtime that builds and runs the Rover Service image locally. No cloud account or infrastructure provisioning is required. |
| **Docker Compose** | The local orchestration tool and `docker-compose.yml` file that start the Rover Service container with `docker compose up`, including the localhost port mapping. |
| **Domain Core** | The inner ring of the hexagonal architecture containing `Validator`, `CommandExecutor`, and `Navigator`. Pure Python with no framework, HTTP, or I/O dependencies. |
| **FastAPI** | The Python 3.12 web framework used by the Rover Service. Provides the `POST /simulate` route, request/response models, and the generated OpenAPI specification. |
| **FastAPI Route Adapter** | The adapter that is the entry point of the Rover Service. Deserialises the `POST /simulate` JSON request body, orchestrates validation and execution, serialises the response, and calls the Logger Adapter. |
| **GitHub Actions** | The CI/CD platform that runs the pipeline on every pull request and merge to `main`. Responsible for lint/security checks, tests, `docker build`, and publishing the image to GHCR. |
| **GitHub Container Registry (GHCR)** | The OCI image registry that stores published Rover Service images. Anyone with Docker can pull a published tag and run it locally. |
| **Logger Adapter** | The adapter that wraps Python's `logging` module to emit a single structured JSON log entry per request to stdout. |
| **MVP** | Minimum Viable Product. The initial scope of the system as defined by FR-1 through FR-7, with no persistence, no authentication, and a single endpoint. |
| **Navigator** | The domain component that handles all three command types. For `F`: checks boundaries and obstacles, returns a new `Position` or a `BlockedMove`. For `L` and `R`: computes and returns the new `Heading`. |
| **OpenAPI** | The OpenAPI 3.x specification generated by FastAPI from the route adapter's request/response models and served at `/openapi.json`. It formally defines the `POST /simulate` request and response schemas (CV-5). |
| **Port** | A Python `Protocol` (structural interface) that defines what the domain core requires from an adapter. No outbound ports exist in the MVP because the core has no external dependencies. |
| **Published Image Tag** | The GHCR identifier for a release, e.g. `ghcr.io/OWNER/rover-service:<git-sha>` (and `latest` on `main`). It replaces cloud deployment environments: pulling and running a tag is the deployment. |
| **Rover Service** | The single deployable unit: a Python 3.12 FastAPI application served by Uvicorn in a Docker container, exposing `POST /simulate`. Contains the FastAPI Route Adapter and the domain core. |
| **Ubiquitous Language** | The shared vocabulary used consistently across code, tests, diagrams, and documentation (CV-4). The terms in this glossary are that vocabulary. |
| **Uvicorn** | The ASGI server that serves the FastAPI application inside the Rover Service container. |
| **Validator** | The domain component that enforces FR-7 input checks. Raises `ValidationError` on the first failing check; does not call any other component. |
