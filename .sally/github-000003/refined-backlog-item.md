# Refined backlog item

Backlog item: GitHub issue #3 - Add dotnet ingestion pipeline

Source: https://github.com/fabioscagliola/Sally/issues/3

## Description

Add a standalone .NET C# ingestion pipeline under `graph-rag/ingestion/dotnet/`. The pipeline must use Roslyn to analyze a supplied .NET project or solution and write the version-1 Graph RAG representation to a JSON file. The version-1 JSON representation is the language-neutral interchange contract between this pipeline and the existing Graph RAG foundation.

The pipeline is intended to make a .NET backend useful for project-context retrieval. It must use Roslyn semantic analysis where necessary to resolve code entities and relationships accurately, rather than relying only on syntax. The initial implementation should capture the smallest useful set of C# entities and relationships needed to represent a backend codebase.

The first validation target is the NerdyWeirdWords backend project. The current target is a `net9.0` ASP.NET Core backend with C# classes including `Program`, controllers, domain classes, a database context, and request models.

The pipeline must remain independent of Neo4j and must not extend the existing Python implementation with language-specific ingestion logic. The existing Graph RAG tooling will consume the generated JSON file. Retrieval, embeddings, and other language-specific ingestion pipelines are outside this backlog item.

## Constraints

- Use Roslyn (`Microsoft.CodeAnalysis`) for C# parsing and semantic analysis.
- Accept a .NET project or solution as the ingestion input.
- Produce a valid version-1 JSON document using the existing Graph RAG representation and its strict serialization contract.
- Write the generated version-1 JSON representation to an explicitly supplied output file; do not introduce an in-process or network handoff boundary.
- Keep graph production independent of Neo4j and the Neo4j writer.
- Use semantic analysis to resolve symbols and relationships where syntax alone is insufficient.
- Capture only these C# entity types: `Project`, `Type`, `Method`, and `Property`.
- Represent classes, interfaces, records, and enums as `Type` entities with a `kind` property.
- Represent constructors as `Method` entities with a corresponding `kind` property.
- Capture only these relationship types: `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE`.
- Do not create entities for parameters, fields, local variables, local functions, namespaces, or source files.
- Validate the pipeline against `fabioscagliola/NerdyWeirdWords`, specifically its `NerdyWeirdWordsBackend` project, using a parameterized local-checkout command.
- Preserve stable source identities and useful source locations so generated graphs can be compared and consumed deterministically.
- Use deterministic project identity combined with Roslyn documentation/declaration IDs for declared symbols. This identity scheme must distinguish overloads, nested and generic types, and same-named members, while merging partial declarations into one entity.
- Do not create entities for framework or package symbols outside the analyzed scope. Emit relationships only when both endpoints are in scope, while preserving useful fully qualified external type information as properties where appropriate.
- Use declaration locations for graph nodes, with normalized portable paths relative to the analyzed project or solution. Relationship/reference locations are not required.
- Apply best-effort ingestion: retain supported declaration entities when possible and skip only relationships whose symbols cannot be resolved. Failure to load the requested project or solution must fail the ingestion. Source-generated documents are out of scope.
- For a `.sln`, ingest all C# projects in the solution. For a `.csproj`, emit entities only for that project; referenced projects may be loaded for semantic resolution but are outside the emitted scope unless selected by the input.
- Do not implement retrieval, embeddings, AI integration, Neo4j persistence, or TypeScript/Markdown/other language pipelines in this item.
- Provide a containerized execution path for the pipeline so it can be built and run without requiring a .NET SDK on the host. The input project or solution and output JSON file must be usable through mounted host paths.

## Assumptions

- The pipeline belongs in the Sally repository as a standalone .NET component under `graph-rag/ingestion/dotnet/`.
- The version-1 JSON representation itself is the cross-language contract; neither the Python foundation nor the C# pipeline exclusively owns the neutral contract.
- The pipeline provides an explicit command or API that accepts an input `.csproj` or `.sln` and an output JSON file path.
- Normal automated tests use checked-in representative C# fixtures and do not require a local NerdyWeirdWords checkout, network access, or a database.
- A separate parameterized validation command may run the pipeline against a caller-supplied local NerdyWeirdWords checkout.
- The initial graph vocabulary is limited to `Project`, `Type`, `Method`, and `Property` entities and `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE` relationships.
- Roslyn documentation/declaration IDs are available for declared symbols and can be combined with deterministic project identity to form stable source IDs.
- Source locations emitted in JSON use one-based line and column values and portable paths relative to the analyzed project or solution.
- Native execution with the .NET SDK may also be supported, but the containerized execution path is the reproducible reference workflow.

## Acceptance criteria

- A Roslyn-based .NET ingestion pipeline exists and accepts a supported `.csproj` or `.sln` input.
- The pipeline loads the input with the required compilation references and produces semantic models for the C# documents it analyzes.
- The pipeline writes a valid version-1 Graph RAG JSON document without importing or depending on Neo4j-specific APIs or types.
- The pipeline accepts an explicit output file path and produces the JSON interchange document there.
- Generated graph nodes have stable source identities, a defined entity type, useful properties, and source-location metadata where source locations are available.
- Generated graph relationships have resolved source and target identities, a defined relationship type, and valid properties where applicable.
- The pipeline captures only `Project`, `Type`, `Method`, and `Property` entities; classes, interfaces, records, and enums are represented as `Type` entities with a `kind` property, and constructors as `Method` entities with a corresponding `kind` property.
- The pipeline captures only `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE` relationships.
- The pipeline uses semantic symbol resolution for containment, inheritance, implementation, method calls, and type usage relationships.
- `USES_TYPE` covers applicable type usages including parameter types, return types, property/field types, and object creation without introducing separate relationship types.
- Parameters, fields, local variables, local functions, namespaces, and source files are not emitted as graph entities.
- External framework and package symbols are not emitted as nodes; relationships to out-of-scope targets are omitted, with useful external type information retained as properties where appropriate.
- The generated representation is deterministic for the same input: node and relationship identities and ordering do not vary between repeated runs absent source changes.
- Unsupported or unresolved syntax/symbol cases follow best-effort policy: supported declaration entities are retained where possible and only affected unresolved relationships are skipped. Failure to load the requested project or solution fails the ingestion.
- For a `.sln`, all C# projects are in the emitted scope; for a `.csproj`, only that project is in the emitted scope, even when referenced projects are loaded for semantic resolution.
- Node source locations use declaration locations with normalized portable paths relative to the analyzed project or solution; relationship/reference locations are not required.
- Running the parameterized validation command against a caller-supplied NerdyWeirdWords checkout produces a non-empty graph containing representative backend entities, including projects, controller/domain types, methods, properties, and the selected relationships.
- Checked-in fixture tests cover contract compatibility, stable identity, partial declarations, overloads, nested/generic types, source locations, representative Roslyn semantic relationships, deterministic output, unsupported/unresolved cases, and project/solution scope.
- Documentation explains how to build and run the standalone pipeline, provide project/solution and output paths, consume the JSON with the existing Graph RAG tooling, and run the optional NerdyWeirdWords validation command.
- Neo4j is not required to build or run the ingestion pipeline tests.
- Retrieval, embeddings, AI integration, and other language-specific ingestion pipelines are not included.
- The pipeline can be built and run in a container against a mounted `.csproj` or `.sln` and writes the generated version-1 JSON document to a mounted output location.

## Questions

- None.