# Refined backlog item

Backlog item:

Create the Graph RAG foundation for Sally using Neo4j.

Source: [GitHub issue #1](https://github.com/fabioscagliola/Sally/issues/1)

## Description

Introduce a reusable Graph RAG foundation that represents a target project's source code and documentation as a disposable graph in Neo4j.

The first implementation is a Python library and command-line interface, not a long-running service. It must provide a common representation that future language-specific ingestion pipelines can produce and submit without depending directly on Neo4j. The initial scope is the graph foundation only; ingestion pipelines for C#, TypeScript, and Markdown are future work.

An ingestion run must be able to delete the existing graph and rebuild it completely from the supplied representation. Incremental updates are explicitly out of scope for this issue.

## Constraints

- Neo4j is the graph store.
- The graph is a disposable, derived representation of a target project's source code and documentation; it is not the system of record.
- The implementation must be a non-running Python library and CLI. It must not introduce a continuously running Sally service.
- Future C#, TypeScript, and Markdown ingestion pipelines must be able to use the common representation without coupling directly to Neo4j.
- The common representation must be technology-independent and support at least typed nodes, typed relationships, stable source identity, and source-location metadata.
- The initial rebuild operation must replace the existing graph in full rather than attempt incremental synchronization.
- A reproducible local Neo4j setup must be provided with Docker Compose.

## Assumptions

- The implementation belongs to the Sally repository.
- Python is the implementation language for the foundation, library API, CLI, and automated tests.
- This issue does not implement source-code or Markdown parsing, language-specific ingestion pipelines, graph retrieval/query workflows, embeddings, or an AI model integration.
- The exact Neo4j version, Python packaging/tooling, graph labels and properties, relationship vocabulary, CLI syntax, and test split can be selected during implementation planning, provided they satisfy the acceptance criteria.
- Tests may use an isolated Neo4j instance or a suitable test double for unit-level behavior; the planning stage must define which behaviors require a real Neo4j integration test.

## Acceptance criteria

- A Python library exposes a common graph representation that can express typed nodes and typed relationships, stable source identity, and source-location metadata without importing or depending on Neo4j-specific types.
- A Neo4j writer component accepts the common representation and persists it to Neo4j; language-specific pipelines can call this component through the library boundary rather than writing Neo4j operations themselves.
- A rebuild operation deletes the existing graph and writes the supplied representation as a complete replacement.
- Rebuilding with the same representation is deterministic and does not leave duplicate graph data from the previous run.
- A CLI invokes the rebuild workflow for a supplied serialized graph representation, with documented invocation and failure behavior.
- Docker Compose starts a local Neo4j instance suitable for development and test execution, with the required configuration documented and no secrets committed.
- Automated tests verify the common representation, Neo4j write behavior, full delete-and-rebuild behavior, and CLI success and failure paths at the level defined by the implementation plan.
- The repository contains documentation describing the foundation’s boundaries, the common representation, how to start Neo4j, how to run the CLI, and how to run the tests.
- No C#, TypeScript, or Markdown ingestion pipeline is required to satisfy this issue.
- No long-running Sally service is required to satisfy this issue.

## Questions

- What exact node and relationship types and source-location fields should the minimal contract define? The implementation plan should propose the smallest useful vocabulary and explain how it can evolve.
- Should the CLI accept a serialized intermediate representation, expose a sample/fixture input, or both? The implementation plan should select the simplest demonstrable interface.
- Which Neo4j operations must be covered by a real integration test, and how should the test database be isolated and cleaned up?
- Should the rebuild be transactional or otherwise fail without leaving a partially rebuilt graph? The implementation plan should define the behavior and its test coverage.

