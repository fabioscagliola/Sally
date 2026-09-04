# Implementation plan

Refined backlog item: [.sally/github-000003/refined-backlog-item.md](.sally/github-000003/refined-backlog-item.md)

## Affected components

- `graph-rag/ingestion/dotnet/`
  - Standalone .NET solution/project for the C# ingestion pipeline, using `IngestDotNet` for the project and assembly.
  - Roslyn project/solution loading, semantic analysis, graph extraction, source-ID generation, and strict version-1 JSON output.
  - Container definition and execution documentation.
- `graph-rag/ingestion/dotnet/src/`
  - Neutral version-1 graph DTOs and serializer matching the cross-language JSON contract used by the existing foundation.
  - Input loading and ingestion orchestration.
  - C# symbol/entity and relationship extraction.
- `graph-rag/ingestion/dotnet/tests/`
  - Self-contained C# fixture projects and automated unit/integration-style tests that do not require NerdyWeirdWords, Neo4j, network access, or a database.
- `graph-rag/ingestion/dotnet/Dockerfile` and supporting scripts/configuration
  - Reproducible .NET SDK container build and mounted input/output execution path.
- `graph-rag/ingestion/dotnet/README.md`
  - Build/run instructions, input scope, graph vocabulary, JSON boundary, testing, container usage, and parameterized NerdyWeirdWords validation.
- `graph-rag/README.md`
  - Add a concise link and boundary note for the .NET ingestion pipeline without moving its detailed instructions into the Python subsystem.

## Implementation approach

Build a standalone `net10.0` .NET component under `graph-rag/ingestion/dotnet/`, using `IngestDotNet` for the project and assembly, `IngestDotNetTest` for the test project, and `ingest-dotnet` for the CLI and container image. No new file, directory, project, assembly, package, namespace, executable, or container image identifier may contain `Sally` or `sally`; branding may appear only in human-facing text or required historical contract values. Keep it independent from Neo4j and other runtimes. The component should expose a small library API for ingestion and a short-lived CLI that accepts an input `.csproj` or `.sln` plus an output JSON file path. It must still load and analyze the `net9.0` NerdyWeirdWords backend target.

Use `Microsoft.Build.Locator` and `Microsoft.CodeAnalysis.Workspaces.MSBuild` to load real project/solution files with their evaluated compilation references. Use Roslyn compilations, syntax trees, semantic models, symbols, and operations to extract the selected graph vocabulary.

The JSON writer should implement the existing version-1 interchange format directly. Its internal DTOs may mirror `GraphDocument`, `GraphNode`, `GraphRelationship`, and `SourceLocation`, but must not reference Neo4j or other runtime-specific types. Serialize the required `format`, `version`, `nodes`, `relationships`, node properties/locations, and relationship properties with deterministic ordering and strict validation implemented natively in .NET. The .NET build and test path must be self-contained. Preserve the existing version-1 format value required by the cross-language contract even though it contains historical project branding. End-to-end validation across the .NET producer, the existing foundation, and Neo4j is a later integration/orchestration backlog item.

Use an explicit ingestion scope:

- `.csproj`: emit one `Project` node and declarations from that project only; load references as needed for semantic resolution.
- `.sln`: load all C# projects and emit one `Project` node plus declarations from every C# project in the solution.

Use project identity plus Roslyn documentation/declaration IDs for declared-symbol source IDs. Build one node per symbol identity, allowing partial declarations to converge. Emit only `Project`, `Type`, `Method`, and `Property` nodes. Represent class/interface/record/enum kind in a `kind` property and constructor kind in a `Method` property. Use normalized portable declaration paths relative to a stable project/solution root and convert Roslyn positions to one-based line and column values.

Extract only `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE` relationships. Traverse declarations and operation/symbol references semantically. Emit a relationship only when its target declaration is in the selected ingestion scope. Do not emit nodes for parameters, fields, local variables, local functions, namespaces, source files, framework symbols, or package symbols. Preserve useful external type names as scalar properties where the contract allows it.

Make extraction best-effort for individual unresolved symbols and compilation diagnostics: retain supported declaration nodes and skip only relationships that cannot be resolved. Treat failure to load or evaluate the requested project/solution as a fatal CLI/library error. Exclude source-generated documents.

Sort projects, nodes, and relationships by stable IDs and relationship fields before serialization. Validate the in-memory graph before writing it, including unique node IDs, valid endpoints, supported property values, and version-1 format/version fields.

## Implementation steps

1. Create the standalone .NET project structure under `graph-rag/ingestion/dotnet/`, targeting `net10.0`, with project/assembly identifier `IngestDotNet`, test project `IngestDotNetTest`, CLI/image identifier `ingest-dotnet`, a library, CLI entry point, fixture projects, Dockerfile, and README. Ensure the component can analyze `net9.0` inputs.
2. Add Roslyn/MSBuild dependencies needed to load `.csproj` and `.sln` inputs and inspect compilations. Register or resolve the MSBuild instance before using `MSBuildWorkspace`.
3. Implement internal version-1 graph DTOs and strict JSON serialization matching the existing cross-language contract, including deterministic ordering, source locations, and scalar/list property restrictions. Validate the contract independently in .NET with no dependency on Python or another runtime. Preserve required historical contract values while keeping all new technical identifiers neutral.
4. Implement input loading for `.csproj` and `.sln`, including C# project filtering, evaluated compilation references, project identity, selected project scope, and fatal load-error handling.
5. Implement stable source-ID generation from deterministic project identity plus Roslyn documentation/declaration IDs. Normalize declaration paths relative to the project/solution root and convert declaration spans to one-based locations.
6. Implement declaration extraction for `Project`, `Type`, `Method`, and `Property` nodes. Map class/interface/record/enum symbols to `Type` nodes with `kind`; map constructors to `Method` nodes with `kind`; exclude the explicitly unsupported declaration categories.
7. Implement semantic relationship extraction for `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE`, including applicable parameter/return/property/field type usages and object creation without emitting parameter or field nodes.
8. Add best-effort handling for unresolved symbols, compilation diagnostics, external symbols, partial declarations, generated documents, and duplicate relationships according to the approved policies.
9. Implement the neutral `ingest-dotnet` short-lived CLI with explicit input/output arguments, actionable fatal errors, and a parameterized validation command or script that accepts a local NerdyWeirdWords checkout path.
10. Add the Dockerfile and documented mounted execution command so the pipeline can build and run without a host .NET SDK. Ensure both input project/solution paths and output JSON paths work through mounted directories.
11. Add checked-in fixture projects covering the selected entity and relationship vocabulary, overloads, nested/generic types, partial declarations, external references, unresolved references, project scope, and solution scope.
12. Add documentation for the JSON boundary, supported vocabulary, deterministic IDs/order, diagnostics policy, CLI arguments, native and containerized workflows, fixture tests, and NerdyWeirdWords validation.
13. Run formatting/static checks, the self-contained .NET test suite, a container build/test, and the parameterized NerdyWeirdWords command when a checkout path is supplied. Defer end-to-end validation across the producer, the existing foundation, and Neo4j to a later integration/orchestration backlog item.

## Tests

- **JSON contract tests:** serialize representative documents and validate the version-1 schema independently with native .NET test code; reject duplicate node IDs, missing relationship endpoints, invalid format/version, unsupported property values, and malformed locations. These tests must not require another runtime, the existing foundation, Neo4j, or network access.
- **Entity extraction tests:** verify projects, classes, interfaces, records, enums, methods, constructors, and properties map to the exact allowed node types and `kind` properties; verify excluded categories do not become nodes.
- **Relationship tests:** verify semantic `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE` relationships for fixture classes; verify `USES_TYPE` covers selected parameter/return/property/field/object-creation usages without creating unsupported nodes.
- **Identity tests:** verify overloads, nested types, generic types, same-named members, and partial declarations produce stable unique IDs with partial declarations merged.
- **Scope tests:** verify `.csproj` input emits only that project's nodes, referenced projects can assist resolution without being emitted, and `.sln` input emits all C# projects.
- **Location and determinism tests:** verify normalized portable declaration paths, one-based positions, stable node/relationship ordering, and byte-equivalent JSON for repeated ingestion of unchanged fixtures.
- **Best-effort tests:** verify unresolved relationships are skipped while unrelated declaration nodes remain, external symbols are not emitted, and source-generated documents are excluded. Verify project/solution load failures are fatal.
- **CLI tests:** verify input/output arguments, malformed input paths, output failures, and non-zero failure behavior. Verify the CLI writes a valid JSON document without requiring Neo4j.
- **NerdyWeirdWords validation:** provide a parameterized command such as `dotnet run --project graph-rag/ingestion/dotnet/src/IngestDotNet/IngestDotNet.csproj -- <checkout>/NerdyWeirdWordsBackend/NerdyWeirdWordsBackend.csproj <output>.json`; assert the result is non-empty and contains representative project, controller/domain type, method, property, and selected relationship nodes/edges. Keep this command separate from normal automated tests.
- **Container test:** build the neutral `ingest-dotnet:local` image and run the CLI with host fixture input/output directories mounted, confirming the output file is created and validates against the version-1 contract using native .NET checks.

Recommended commands, subject to the final project/CLI names:

```bash
dotnet test graph-rag/ingestion/dotnet/tests/IngestDotNetTest/IngestDotNetTest.csproj
docker build -t ingest-dotnet:local graph-rag/ingestion/dotnet
docker run --rm -v "$PWD":/workspace ingest-dotnet:local \
  /workspace/<input>.csproj /workspace/<output>.json
```

## Questions

- None.