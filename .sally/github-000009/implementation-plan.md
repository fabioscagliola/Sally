# Implementation plan

Refined backlog item: [.sally/github-000009/refined-backlog-item.md](.sally/github-000009/refined-backlog-item.md)

## Affected components

- `graph-rag/README.md`
  - Add a short section describing the new TypeScript ingestion producer and its Docker-based workflow.
  - Keep the existing Neo4j and neutral-JSON documentation boundary unchanged.
- `graph-rag/ingestion/`
  - Add a new TypeScript-oriented ingestion component alongside the existing .NET pipeline, likely under `graph-rag/ingestion/typescript/`.
  - Add project configuration, a Dockerfile, and a small CLI entry that accepts a `tsconfig.json` plus output path.
- `graph-rag/ingestion/typescript/`
  - Add the standalone TypeScript producer and its TypeScript/Node-based unit tests and fixtures.
  - Keep the primary test harness on the TypeScript/Node toolchain rather than on Python.
- `graph-rag/tests/`
  - Extend only where useful for cross-runtime contract compatibility validation of produced JSON.
  - Include a real-project validation path against the NerdyWeirdWords frontend project without modifying that repository.

## Implementation approach

Treat the TypeScript producer as a standalone ingestion component that emits the existing neutral Graph RAG JSON contract directly rather than a Neo4j-specific representation. The producer must not have a runtime dependency on the Python Graph RAG implementation; the Python `GraphDocument` and serialization code may only be used in compatibility or regression tests where the produced JSON is validated against the same contract.

The implementation should follow the same high-level pattern as the C# pipeline:

1. Discover the TypeScript project root from the supplied `tsconfig.json`, while keeping the repository root distinct from that compiler project root.
2. Parse the compiler project with the TypeScript Compiler API.
3. Filter the analyzed source set to the configured project scope, excluding declaration files, dependency/compiler/library sources, and other sources outside the project scope selected by `tsconfig.json`.
4. Materialize semantic nodes only for the supported TypeScript concepts: `Project`, `Type`, `Function`, `Method`, and `Property`.
5. Emit only the allowed relationship types already used by the neutral graph contract: `CONTAINS`, `CALLS`, `USES_TYPE`, `INHERITS`, and `IMPLEMENTS` where they are semantically valid.
6. Write a deterministic, contract-valid JSON document to an explicitly supplied output path.
7. Validate the output with compatibility/regression tests and with a real project smoke test on the NerdyWeirdWords frontend.

The most important technical constraint is preserving the Graph RAG boundary: the TypeScript producer must not depend on Neo4j or the Python runtime, should not invent any new schema, and should avoid React-specific or retrieval-specific concepts.

## Implementation steps

1. Confirm the exact TypeScript project entry points and Docker packaging pattern to match the existing .NET ingestion workflow.
2. Add the new TypeScript ingestion package under `graph-rag/ingestion/typescript/` with a CLI or entry script that accepts a `tsconfig.json` path and an output JSON path.
3. Implement a thin project-loader layer that reads the TypeScript configuration, resolves the compiler program, and filters out declaration files, dependency/compiler/library sources, and other project-excluded inputs selected by `tsconfig.json`.
4. Add a deterministic symbol collector that walks the TypeScript AST and emits only supported entities:
   - project root as `Project`
   - named TypeScript declarations as `Type` nodes, with a `kind` indicator where needed
   - named function declarations and named variable-bound arrow/function expressions as `Function` nodes where applicable
   - methods as `Method`
   - class fields and similar properties as `Property`
   - do not emit arbitrary anonymous callbacks as standalone `Function` nodes
5. Create stable node IDs from a stable project identity combined with paths relative to the TypeScript project root and declaration identity so repeated runs are deterministic and multiple TypeScript projects can coexist in the unified graph; emit source locations relative to the repository root so they remain consistent with the common Graph RAG model and future unified cross-source graph usage.
6. Add semantic relationship extraction using compiler symbols rather than raw text matching, with explicit handling for:
   - `CONTAINS`
   - `CALLS`
   - `USES_TYPE`
   - `INHERITS`
   - `IMPLEMENTS`
7. Exclude unsupported constructs and out-of-scope targets, while preserving useful type information only when both endpoints are in the selected project scope.
8. Serialize the final graph using the same neutral Graph RAG JSON contract used elsewhere in the repo, ensuring strict validation passes.
9. Add focused tests for representative TypeScript patterns and a small checked-in fixture that exercises the supported graph semantics without requiring a real external project.
10. Add a dockerized execution path so the tool can run without a host-installed TypeScript toolchain.
11. Run the real-project validation against the NerdyWeirdWords frontend and confirm the generated JSON is non-empty and contains the expected project structure and relationship patterns, without modifying that repository.

## Tests

- **Fixture-based unit tests (TypeScript/Node harness):**
  - verify the TypeScript compiler project loads from a `tsconfig.json`
  - ensure declaration and dependency files are excluded
  - verify supported entity types are emitted and unsupported nodes are skipped
  - assert deterministic IDs and repository-relative source locations
- **Relationship tests:**
  - check `CONTAINS` for nested declarations
  - check `CALLS` for direct function/method invocation
  - check `USES_TYPE` for type references and property signatures
  - check `INHERITS` and `IMPLEMENTS` for class/interface relationships where applicable
- **Contract regression tests:**
  - run the existing Graph RAG contract and serialization tests unchanged
  - validate the generated TypeScript output against the same strict JSON schema
- **Docker smoke tests:**
  - verify the project can be built and run from a container without host-side TypeScript tooling
- **Real-project validation:**
  - run the ingestor against the NerdyWeirdWords frontend and confirm output includes representative project, type, function, method, and property entities

Recommended commands:

```bash
cd graph-rag
pytest -m 'not integration'
# run the new TypeScript ingestion tests and contract checks
# validate Docker execution for the TypeScript producer
# run a smoke validation against a local NerdyWeirdWords checkout
```

## Questions

- None. The refined backlog item is specific enough to proceed without blocking ambiguity.
