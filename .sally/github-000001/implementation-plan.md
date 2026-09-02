# Implementation plan

Refined backlog item: [.sally/github-000001/refined-backlog-item.md](.sally/github-000001/refined-backlog-item.md)

## Affected components

- `graph-rag/pyproject.toml`: Define the self-contained Python package, supported Python version, runtime dependency on the Neo4j driver, test dependencies, and the `graph-rag-cli` entry point.
- `graph-rag/src/graph_rag/`: Package containing the technology-independent graph contract, serialization support, Neo4j adapter, and rebuild orchestration.
- `graph-rag/src/graph_rag/cli.py`: Non-running command-line entry point that reads a serialized graph representation and invokes the rebuild workflow.
- `graph-rag/tests/`: Unit tests for the contract, serialization, orchestration, and CLI, plus explicitly marked Neo4j integration tests.
- `graph-rag/compose.yaml`: Reproducible local Neo4j development and integration-test dependency with configuration supplied through `NEO4J_*` environment variables.
- `graph-rag/fixtures/`: Serialized version-1 graph representation used by examples, CLI tests, and integration tests.
- `graph-rag/README.md`: Detailed subsystem documentation covering the foundation’s boundary, graph contract, local Neo4j setup, CLI usage, test commands, and future work boundaries.
- `graph-rag/.gitignore`: Exclude Python caches, virtual environments, test output, and local environment files as appropriate.
- Repository-root `README.md`: Add or update a concise link and orientation for the Graph RAG subsystem without moving its detailed documentation into the repository root.

## Implementation approach

Build a small, self-contained Python subsystem under `graph-rag/`, with a clean boundary between graph production and graph persistence. The subsystem must be runnable from its own directory and must not turn the Sally repository itself into a Python project:

1. Define immutable, JSON-serializable dataclasses for a graph document, nodes, relationships, and source locations. A node should have a stable source identity, a caller-defined type, properties, and optional source-location metadata. A relationship should have a caller-defined type, source and target node identities, and optional properties. Keep these models free of Neo4j imports.
2. Validate the representation at the boundary: node identities must be unique, relationship endpoints must exist, types must be non-empty, and serialized input must reject malformed or ambiguous data with actionable errors. Preserve property values that Neo4j can represent, or define and test a narrow supported JSON value set.
3. Serialize and deserialize the representation as a strict version-1 JSON document. Use a top-level format/version field and reject unknown or malformed fields clearly. The CLI will accept a path to this serialized representation; include a checked-in fixture under `graph-rag/fixtures/` for demonstration.
4. Implement a Neo4j adapter behind a package-owned interface. The adapter maps the neutral representation to parameterized Cypher and uses stable source identities for deterministic `MERGE` behavior. Do not expose Neo4j driver sessions, transactions, or node objects through the neutral API.
5. Implement rebuild as one explicit write transaction against the default database of the dedicated disposable Compose instance: delete existing nodes with `DETACH DELETE`, then write the supplied nodes and relationships. Rollback on an error so a failed rebuild does not intentionally leave a partial result. Document that this database is wholly owned by the derived graph because the delete is destructive.
6. Keep the CLI short-lived and name its executable `graph-rag-cli`: read Neo4j connection defaults from `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`, allow optional CLI flags to override them, connect, validate, rebuild, close the driver, and return a non-zero exit code with a concise error on invalid input or connection/write failure. Use `argparse` unless an existing dependency proves necessary.
7. Provide a Docker Compose Neo4j service for local development and integration tests. Use the default database in this dedicated disposable instance, keep credentials/configuration out of source control, provide safe local defaults or an `.env.example`, expose only the ports needed by the workflow, and add a health check so tests can wait for readiness.

The initial schema is deliberately generic: use `:Entity` nodes with a `type` property, a stable `source_id`, optional `source_uri`, and optional location fields (`start_line`, `start_column`, `end_line`, `end_column`). Use one generic `:RELATES_TO` relationship type with its own `type` property. For example, a method call is represented as `(:Entity {type: "Method"})-[:RELATES_TO {type: "CALLS"}]->(:Entity {type: "Method"})`. Keep Cypher identifiers fixed and values parameterized. Avoid claiming semantic C#, TypeScript, or Markdown ingestion support until those pipelines are implemented in separate backlog items.

## Implementation steps

1. Establish the complete `graph-rag/` package layout, including `pyproject.toml`, `src/`, `tests/`, `fixtures/`, Compose configuration, and subsystem documentation. Define the supported Python version, dependency groups, `graph-rag-cli` entry point, and separate unit/integration test commands. Select a maintained Neo4j Python driver version compatible with the supported Python version.
2. Implement the neutral graph contract and its validation rules. Include source-location metadata as optional structured fields and define the supported JSON/property value types.
3. Implement strict version-1 JSON serialization/deserialization and a representative fixture under `graph-rag/fixtures/` containing multiple nodes and relationships, including source locations. Reject unknown or malformed fields clearly.
4. Define a small writer protocol and implement the Neo4j adapter using fixed `:Entity` and `:RELATES_TO` Cypher structure, parameterized values, stable identity constraints/indexes where appropriate, and explicit driver lifecycle management.
5. Implement the full rebuild use case as one transaction against the default database. Ensure the graph is replaced rather than appended, repeated identical input is deterministic, and failures roll back the transaction.
6. Implement `graph-rag-cli` for a serialized representation path. Read `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE` from the environment and support optional CLI overrides; provide clear exit codes/messages for malformed input, unreachable Neo4j, and write failures.
7. Add the dedicated disposable Docker Compose Neo4j instance under `graph-rag/`, with a health check, `NEO4J_*` configuration, and any initialization needed for the default database.
8. Add subsystem documentation under `graph-rag/` covering installation, starting/stopping Neo4j, the version-1 contract, the fixture, CLI environment variables and overrides, running unit tests without Neo4j, and running the separate Docker-backed integration suite. Add only a concise subsystem link/orientation to the repository-root README where appropriate.
9. Run formatting, static checks if selected, the unit-test command from `graph-rag/`, and the Docker-backed integration-test command from `graph-rag/`; resolve only issues introduced by this implementation.

## Tests

- Contract unit tests: construct valid graphs; reject duplicate node identities, missing relationship endpoints, invalid types, unsupported properties, and malformed source locations.
- Serialization tests: round-trip the `graph-rag/fixtures/` fixture without semantic changes; reject unknown/missing required fields under the strict version-1 policy; verify stable JSON behavior where deterministic output is promised.
- Writer/orchestration unit tests: use a fake writer or mocked driver boundary to verify that rebuild requests deletion followed by the complete supplied representation, closes resources, and propagates failures.
- CLI tests: successful `graph-rag-cli` invocation with the fixture; missing/unreadable input; invalid JSON/contract; missing `NEO4J_*` configuration; CLI override precedence; and Neo4j failure all produce documented non-zero behavior without a traceback intended for end users.
- Neo4j integration tests, marked separately and run only through a clearly documented Docker-backed command: write a graph and query back node/relationship counts and representative properties; rebuild after seeding stale data and confirm stale nodes/relationships are gone; rebuild the same input twice and confirm counts and identities do not duplicate; force a write failure where practical and verify transaction rollback semantics.
- Test isolation: run integration tests only against the default database of the dedicated disposable Compose Neo4j instance, never a developer’s shared graph. The suite must clean up its data and document the required Docker/Compose command and environment variables. The normal unit-test command must not require Neo4j or Docker.

## Questions

- **Integration failure injection:** Determine the most reliable local test mechanism for provoking a write failure while preserving meaningful rollback assertions.
- **Scope boundary:** Retrieval, embeddings, and language-specific ingestion are explicitly separate backlog items. This implementation must not add those capabilities or fold their documentation into the subsystem.

