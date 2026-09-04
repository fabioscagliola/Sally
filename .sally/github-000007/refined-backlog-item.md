# Refined backlog item

Backlog item: GitHub issue #7 - Remove the common `Entity` label from nodes persisted by the Graph RAG Neo4j writer

Source: https://github.com/fabioscagliola/Sally/issues/7

## Description

Remove the common `Entity` label from every graph node persisted by the Graph RAG Neo4j writer. The Neo4j database is dedicated to the disposable derived project graph, so generic operations across all graph nodes can use unlabeled node matching.

Each node must be persisted with only the native Neo4j label supplied by the node's semantic `type`. For example:

```cypher
(:Method {type: "Method"})
(:Type {type: "Type"})
(:Property {type: "Property"})
(:Project {type: "Project"})
```

The writer must continue to preserve the original semantic `type` as a node property. Semantic labels remain generic and data-driven: the writer must pass each contract-valid semantic type to Neo4j through parameterized dynamic-label syntax without maintaining a vocabulary or sanitizing, normalizing, renaming, prefixing, suffixing, or otherwise transforming the value.

Relationship persistence remains unchanged. Each relationship continues to use its semantic `type` as the native Neo4j relationship type and retains its existing properties, including the `type` property.

Generic node operations that currently match `Entity` must use unlabeled matching. This includes relationship endpoint lookup during rebuild and any tests, fixtures, queries, or documentation that rely on the common label.

The technology-independent graph representation, version-1 JSON serialization contract, .NET ingestion pipeline, and generated ingestion JSON remain unchanged. Retrieval, embeddings, ingestion pipeline changes, graph vocabulary changes, relationship mapping changes, and graph format identifier changes are outside this backlog item.

## Constraints

- Update Neo4j persistence behind the existing graph writer/rebuild boundary.
- Persist every node with exactly one native Neo4j label: the node's semantic `type` value.
- Do not introduce a replacement common technical label such as `GraphNode`.
- Pass semantic node types through parameterized dynamic-label syntax exactly as supplied by the technology-independent graph representation.
- Do not hard-code the current C# node vocabulary or any other list of recognized labels.
- Do not sanitize, normalize, rename, prefix, suffix, escape into a different value, or otherwise transform semantic type values.
- Preserve each node's original semantic `type` property unchanged, along with all other node and source-location properties.
- If Neo4j rejects a contract-valid semantic label, raise a writer-contextual error that identifies the rejected semantic type and retains the original Neo4j exception as its cause.
- Use unlabeled node matching for generic operations across persisted graph nodes, including relationship endpoint lookup.
- Keep semantic relationship types and all relationship properties unchanged.
- Keep full delete-and-rebuild behavior transactional, deterministic, and idempotent.
- Remove repository-managed `Entity`-specific indexes or constraints if any are found; the current repository contains none.
- Do not add runtime migration behavior to discover or remove externally created or legacy schema objects already present in a database.
- Do not introduce per-semantic-type indexes or constraints.
- Keep the technology-independent graph representation and strict version-1 JSON serialization contract unchanged.
- Keep the .NET ingestion pipeline code and its generated JSON unchanged.
- Do not implement retrieval, embeddings, ingestion pipeline changes, graph vocabulary changes, relationship mapping changes, or graph format identifier changes.
- Do not modify the source GitHub issue.

## Assumptions

- The implementation is confined primarily to `graph-rag/src/graph_rag/writer.py`, its unit and Neo4j integration tests, and Graph RAG documentation that describes or queries the `Entity` label.
- The existing unlabeled full-delete query already has the required generic behavior and does not need a semantic change.
- Relationship endpoint matching can rely on globally unique node `source_id` values guaranteed by the validated graph document and the rebuild transaction.
- The existing transaction boundary rolls back the delete-and-rebuild operation if Neo4j rejects a dynamic semantic label.
- No fixture or .NET ingestion output change is required unless a fixture itself contains a Neo4j-specific `Entity` dependency.
- The supported disposable Neo4j environment provides parameterized dynamic-label syntax for node creation and matching.

## Acceptance criteria

- After rebuild, every persisted graph node has exactly one label equal to its original semantic `type` value and does not have the `Entity` label.
- The writer uses the node's semantic `type` value through parameterized dynamic-label syntax and does not interpolate it into Cypher text.
- Semantic node labels are not hard-coded to `Project`, `Type`, `Method`, `Property`, or any other vocabulary.
- Semantic type values are not sanitized, normalized, renamed, prefixed, suffixed, or otherwise transformed before being used as labels.
- Each persisted node retains a `type` property exactly equal to its original semantic type, along with its existing properties and source-location data.
- No replacement common label such as `GraphNode` is added.
- Relationship endpoint lookup and every other generic graph-node operation in the affected code use unlabeled node matching.
- Existing semantic relationship types, relationship `type` properties, and other relationship properties remain unchanged.
- When Neo4j rejects a contract-valid semantic label, persistence fails with an error that identifies the rejected type, retains the Neo4j exception as its cause, and does not retry with a transformed or fallback label.
- A failed rebuild caused by a rejected label does not leave a partially rebuilt graph.
- Rebuilding the same graph repeatedly produces the same nodes and relationships without duplicates.
- Rebuilding with a different graph removes stale nodes and relationships from the previous graph.
- No repository-managed `Entity`-specific index or constraint remains.
- No per-semantic-type index or constraint is introduced.
- The technology-independent graph representation and strict version-1 JSON serialization contract are unchanged.
- The .NET ingestion pipeline code and generated version-1 JSON are unchanged.
- Unit tests verify unlabeled generic matching, parameterized dynamic semantic labels, unchanged node type parameters, unchanged relationship mapping, and contextual failure behavior.
- Neo4j integration tests verify exact node labels, preserved node `type` properties, absence of the `Entity` and replacement common labels, unchanged relationship types/properties, and deterministic rebuild behavior.
- Integration coverage includes a semantic node type outside the current C# vocabulary to demonstrate that label mapping is data-driven.
- Graph RAG documentation and affected example queries describe nodes as using only their semantic Neo4j labels.
- Existing Graph RAG unit tests pass.
- Existing Neo4j integration tests pass against the disposable local Neo4j instance.

## Questions

- None.