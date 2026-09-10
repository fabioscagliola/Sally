# Refined backlog item

Backlog item: GitHub issue #9 - Add a TypeScript ingestion pipeline to Graph RAG

Source: https://github.com/fabioscagliola/Sally/issues/9

## Description

Add a TypeScript ingestion pipeline under the existing Graph RAG project that analyzes a TypeScript codebase using the TypeScript Compiler API and emits the current language-neutral Graph RAG JSON representation already used by the .NET ingestion pipeline.

The new pipeline must accept a `tsconfig.json` as the project input, parse the project’s source files, and produce semantic Graph RAG nodes and relationships that match the existing strict JSON contract. It must do so without introducing Neo4j-specific behavior, without adding React-specific graph concepts, and without changing retrieval or persistence behavior outside the ingestion producer.

The initial implementation is intentionally scoped to the TypeScript concepts needed by the current Nerdy frontend, focusing on `Project`, `Type`, `Function`, `Method`, and `Property` entities and on relationships such as `CONTAINS`, `CALLS`, `USES_TYPE`, `INHERITS`, and `IMPLEMENTS` where they are semantically applicable.

The first validation target is the real frontend in `fabioscagliola/NerdyWeirdWords`, used to confirm the pipeline can ingest an actual TypeScript project and emit a usable graph without requiring the TypeScript toolchain on the host machine. The implementation must remain independent of Neo4j and must only generate the same Graph RAG JSON contract already produced by the existing .NET ingestion pipeline.

## Constraints

- Use the TypeScript Compiler API to analyze a TypeScript project rooted at a supplied `tsconfig.json`.
- Accept only the project input and produce the existing common Graph RAG JSON representation, not a Neo4j-specific format.
- Exclude declaration files, dependency sources, compiler/library sources, and other sources outside the configured project scope. Respect the project’s tsconfig.json file selection rather than introducing ad hoc file-discovery rules.
- Emit only the initial TypeScript entity types needed for the current Nerdy frontend: `Project`, `Type`, `Function`, `Method`, and `Property`.
- Emit only the supported relation types already used by the Graph RAG contract: `CONTAINS`, `CALLS`, `USES_TYPE`, `INHERITS`, and `IMPLEMENTS` when they are semantically valid.
- Represent named TypeScript declarations such as classes, interfaces, type aliases, and enums as Type nodes, using properties such as kind where needed to preserve the distinction. Do not emit anonymous or compiler-synthesized types as standalone nodes.
- Generate stable, deterministic node IDs for repeated runs of the same input.
- Preserve repository-relative source locations so emitted graph nodes remain traceable to the analyzed project.
- Keep the ingestion producer independent of Neo4j and independent of the writer/persistence layer.
- Produce the same strict Graph RAG JSON contract used by the existing .NET ingestion pipeline; do not invent a TypeScript-specific schema.
- Support running the ingestion pipeline in Docker without requiring the host machine to have the TypeScript toolchain installed.
- Include focused automated tests and a small TypeScript fixture to validate the ingestor.
- Validate against the real `NerdyWeirdWords` frontend project as the intended end-to-end target.
- Do not introduce React-specific graph concepts, cross-source relationships, incremental ingestion, retrieval changes, or additional persistence behavior.
- Do not broaden the scope to other languages, retrieval changes, embeddings, or persistence implementation.

## Assumptions

- The existing Graph RAG JSON contract is already the canonical interchange format for this ingestion producer.
- The TypeScript ingestion pipeline is a standalone producer that writes JSON files and is not coupled to Neo4j or to the Python foundation runtime.
- The project input is a TypeScript project described by a `tsconfig.json`, and source discovery will be based on the compiler project configuration rather than a custom ad hoc file enumeration rule.
- The initial graph vocabulary is intentionally limited to the TypeScript concepts currently needed by the Nerdy frontend, not a complete TypeScript semantic model.
- Deterministic IDs can be derived from stable project and source identities while preserving repository-relative paths and symbol identity.
- The implementation may use compiler semantics to resolve symbols and relationships without needing a host-installed TypeScript toolchain when run via Docker.
- Existing .NET ingestion behavior and Graph RAG contract semantics are the default reference point for TypeScript relationship mapping and output shape.

## Acceptance criteria

- A TypeScript ingestion pipeline exists that accepts a TypeScript project via a `tsconfig.json` input.
- The pipeline analyzes the project with the TypeScript Compiler API and excludes declaration files, dependency sources, compiler/library sources, and other sources outside the configured project scope.
- The pipeline emits `Project`, `Type`, `Function`, `Method`, and `Property` nodes as needed for the current Nerdy frontend and does not invent additional graph concepts.
- The pipeline emits `CONTAINS`, `CALLS`, `USES_TYPE`, `INHERITS`, and `IMPLEMENTS` relationships where they are semantically applicable.
- Node IDs are deterministic and stable across repeated runs for the same input.
- Preserved source locations remain repository-relative and useful for traceability.
- The output JSON matches the same strict Graph RAG JSON contract used by the existing .NET ingestion pipeline.
- The pipeline stays independent of Neo4j and does not require the TypeScript toolchain on the host when run in Docker.
- The pipeline includes focused automated tests and a small checked-in TypeScript fixture.
- Real-project validation against the `NerdyWeirdWords` frontend succeeds and produces meaningful graph output for the initial scope.
- No React-specific concepts, cross-source relationships, retrieval changes, incremental ingestion behavior, or persistence changes are introduced in this issue.

## Questions

1. No blocking questions at this time. The issue provides enough scope, constraints, and validation target to proceed with implementation planning.
