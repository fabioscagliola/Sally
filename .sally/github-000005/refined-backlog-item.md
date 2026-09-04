# Refined backlog item

Backlog item: GitHub issue #5 - Improve Neo4j graph mapping

Source: https://github.com/fabioscagliola/Sally/issues/5

## Description

Improve the Neo4j persistence mapping used by the Graph RAG foundation.

The current Neo4j writer persists every graph node with only the common `Entity` label and every graph relationship with only the generic `RELATES_TO` relationship type. The version-1 graph representation already carries semantic node and relationship types. The Neo4j writer must persist those semantic types using native Neo4j labels and relationship types while keeping the technology-independent graph representation and strict JSON serialization contract unchanged.

For every graph node, Neo4j persistence must:

- keep the common `Entity` label;
- add the graph node's semantic `type` as an additional Neo4j label;
- keep the node's `type` property.

For example, a graph node with `type: "Method"` must be persisted as a Neo4j node equivalent to:

```cypher
(:Entity:Method {type: "Method", ...})
```

For every graph relationship, Neo4j persistence must:

- use the graph relationship's semantic `type` as the native Neo4j relationship type instead of `RELATES_TO`;
- keep the relationship's `type` property.

For example, a graph relationship with `type: "CALLS"` must be persisted as a Neo4j relationship equivalent to:

```cypher
[:CALLS {type: "CALLS", ...}]
```

The mapping must be generic. It must use the semantic types supplied by the version-1 graph representation and must not hard-code the current C# ingestion vocabulary. A graph produced by the .NET ingestion pipeline should therefore produce native labels such as `Project`, `Type`, `Method`, and `Property`, and native relationship types such as `CONTAINS`, `CALLS`, `INHERITS`, and `USES_TYPE`.

Retrieval, embeddings, ingestion pipelines, graph vocabulary changes, and graph format identifier changes are outside this backlog item.

## Constraints

- Keep the technology-independent version-1 graph representation unchanged.
- Keep the strict JSON serialization contract unchanged, including the existing `format` and `version` fields.
- Update Neo4j persistence only behind the existing graph writer/rebuild boundary.
- Preserve the common `Entity` label on every persisted node.
- Preserve each node's semantic `type` property and all existing node properties/source-location properties.
- Add each node's semantic `type` as an additional native Neo4j label.
- Replace the generic persisted `RELATES_TO` relationship type with the relationship's semantic `type`.
- Preserve each relationship's semantic `type` property and all existing relationship properties.
- Keep the mapping generic and driven by graph document values, not by a hard-coded list of current node or relationship types.
- Do not restrict semantic type values to a Neo4j identifier-safe subset beyond the existing version-1 contract's non-empty string validation.
- Safely escape semantic type values when interpolating them into Cypher labels or relationship types.
- Preserve the original semantic type value exactly in the `type` property; do not sanitize, normalize, or rename semantic type values.
- If Neo4j cannot represent an escaped semantic type value, fail persistence clearly rather than silently changing it.
- Do not introduce new indexes or constraints for semantic labels or relationship types in this item.
- Preserve the existing generic identity/indexing behavior.
- Keep full delete-and-rebuild semantics deterministic and idempotent.
- Do not implement retrieval, embeddings, ingestion pipeline changes, graph vocabulary changes, or graph format identifier changes.
- Do not modify the source GitHub issue.

## Assumptions

- The primary implementation area is the existing Python Graph RAG foundation under `graph-rag/src/graph_rag/`, especially `writer.py`.
- Existing unit tests in `graph-rag/tests/test_writer.py`, integration tests in `graph-rag/tests/integration/test_neo4j.py`, the sample fixture, and Graph RAG documentation need updates.
- The persisted graph should remain queryable through the common `Entity` label for compatibility with generic graph operations.
- Native Neo4j labels and relationship types must be constructed by escaping the exact semantic type values safely to avoid invalid Cypher or injection vulnerabilities.
- The existing fixture can be updated to include semantic types representative of the current .NET ingestion output, provided the version-1 contract remains unchanged.

## Acceptance criteria

- The Neo4j writer persists each graph node with both the common `Entity` label and a native label derived from the node's semantic `type`.
- The Neo4j writer retains each node's `type` property after adding the semantic label.
- The Neo4j writer persists each graph relationship using a native relationship type derived from the relationship's semantic `type` instead of `RELATES_TO`.
- The Neo4j writer retains each relationship's `type` property after switching to semantic native relationship types.
- The mapping is generic and works for any valid semantic graph type accepted by the version-1 contract; it does not branch on or hard-code `Project`, `Type`, `Method`, `Property`, `CONTAINS`, `CALLS`, `INHERITS`, `IMPLEMENTS`, or `USES_TYPE`.
- Semantic type values are escaped safely when used as native Neo4j labels or relationship types, while the original values are retained exactly in `type` properties.
- Persistence fails with a clear error when Neo4j cannot represent a semantic type value as a native label or relationship type.
- No new indexes or constraints are introduced for semantic labels or relationship types.
- Rebuilding the same graph repeatedly remains deterministic and does not create duplicate nodes or relationships.
- Rebuilding with a different graph still removes stale nodes and relationships from the previous graph.
- The technology-independent contract and JSON serialization format are unchanged.
- Unit tests verify the Cypher/query construction and parameters for semantic labels and relationship types without requiring Neo4j.
- Integration tests verify Neo4j contains semantic labels and native semantic relationship types after rebuild.
- Integration tests verify generic `Entity` node queries still work after semantic labels are added.
- Integration tests verify `RELATES_TO` is no longer used for persisted semantic relationships.
- Fixtures and documentation are updated to describe the new native Neo4j mapping.
- Existing Graph RAG unit tests pass.
- Existing Neo4j integration tests pass when run against the disposable local Neo4j instance.