# Implementation plan

Refined backlog item: [.sally/github-000007/refined-backlog-item.md](.sally/github-000007/refined-backlog-item.md)

## Affected components

- `graph-rag/src/graph_rag/writer.py`
  - Remove `Entity` from node creation and relationship endpoint matching.
  - Write nodes in deterministic groups by exact semantic type so label rejection can report the responsible value.
  - Add a writer-specific persistence error that retains the rejected type and original Neo4j cause.
- `graph-rag/tests/test_writer.py`
  - Update fake-transaction assertions for semantic-only labels, unlabeled endpoint matching, grouped writes, unchanged parameters, relationship behavior, and contextual failures.
- `graph-rag/tests/integration/test_neo4j.py`
  - Verify exact semantic-only labels, generic unlabeled queries, preserved properties and relationships, arbitrary semantic types, rebuild idempotence, stale-data removal, and transaction rollback where the pinned Neo4j version permits a stable rejection case.
- `graph-rag/README.md`
  - Replace the common-plus-semantic label description and example with semantic-only labels and unlabeled generic matching guidance.

No changes are planned for the graph contract, serialization, sample JSON fixture, .NET ingestion pipeline, generated JSON, schema setup, or CLI. The current repository defines no `Entity`-specific index or constraint to remove, and the CLI already displays propagated writer errors.

## Implementation approach

Keep `GraphDocument`, validation, serialization, relationship mapping, and the managed rebuild transaction unchanged. Change the node query from creating `(:Entity)` and subsequently applying a semantic label to creating a node directly with one parameterized dynamic semantic label:

```cypher
MERGE (entity:$($semantic_type) {source_id: node.source_id})
```

Continue to set `entity.type` from the unchanged node parameter and preserve all source-location and arbitrary node properties. Match relationship endpoints generically by `source_id`:

```cypher
MATCH (source {source_id: relationship.source_id})
MATCH (target {source_id: relationship.target_id})
```

The validated document guarantees unique node source IDs, and full rebuild owns the disposable database contents, so endpoint matching does not require a common label.

Partition node parameters by their exact semantic `type`, process type groups in sorted order, and issue one parameterized `UNWIND` node query per distinct type inside the existing transaction. This preserves data-driven labels without Cypher interpolation and lets the writer associate a Neo4j label/query rejection with one exact semantic type. Catch the applicable non-retriable Neo4j client/query exception around each grouped node write and raise a writer-specific persistence exception that names the type and chains the Neo4j exception. Do not catch or transform unrelated/transient Neo4j failures in a way that disables managed-transaction retry behavior.

Before finalizing the error test, verify which contract-valid semantic type, if any, the pinned `neo4j:5-community` server rejects through dynamic-label syntax. Neo4j accepts label strings that are not static-Cypher identifiers, including punctuation and whitespace, so those values demonstrate exact pass-through rather than failure. If the pinned server has no stable contract-valid rejected value, cover rejection deterministically with a failing unit-test transaction and document that the integration suite cannot manufacture that server condition without changing the contract or relying on version-specific limits.

Do not add schema migration logic, indexes, constraints, fallback labels, type normalization, or a hard-coded semantic vocabulary. Preserve atomic rollback through the existing managed transaction.

## Implementation steps

1. Run a focused query against the pinned Compose Neo4j image to confirm direct parameterized dynamic labels in `MERGE`, broad exact semantic label values, and whether a stable contract-valid rejected label exists.
2. Add a focused writer persistence exception carrying the rejected semantic type, with a clear string representation suitable for the existing CLI error output.
3. Group node parameters by exact `type` and iterate over sorted type keys to keep query order deterministic.
4. Replace `MERGE (entity:Entity ...)` plus `SET entity:$(node.type)` with direct parameterized dynamic-label `MERGE` for each group. Keep `type`, location, and arbitrary property assignment unchanged.
5. Wrap only the grouped node-write rejection that represents Neo4j refusing the semantic label; chain the original exception and do not retry with a changed or fallback label.
6. Remove `Entity` from both relationship endpoint matches while leaving dynamic relationship types, relationship identity, the relationship `type` property, and arbitrary relationship properties unchanged.
7. Update writer unit tests and fakes for the additional query per distinct node type, deterministic group ordering, exact type pass-through, unlabeled endpoint matching, and contextual exception chaining.
8. Update integration assertions to inspect `labels(entity)` and prove each node has exactly its semantic label, no `Entity` or replacement common label exists, node `type` values are preserved, and unlabeled generic queries find all nodes.
9. Extend integration coverage with a semantic type outside the C# vocabulary and retain the existing relationship, repeated-rebuild, and stale-data checks. Add the failed-rebuild rollback case if step 1 identifies a stable server rejection input.
10. Update the README persistence example and wording. Leave fixtures and ingestion artifacts unchanged unless a final scoped search reveals a Neo4j-specific `Entity` dependency.
11. Run the non-integration suite, the focused Compose integration suite, and a final scoped search for persistence-specific `Entity` labels or schema definitions.

## Tests

- **Writer query tests:** verify deletion remains first; each exact semantic type produces one node write with `MERGE (entity:$($semantic_type) ...)`; semantic values remain parameters rather than Cypher interpolation; node properties remain unchanged; and relationship endpoints use unlabeled `source_id` matches.
- **Deterministic grouping tests:** provide interleaved nodes with repeated types and assert one query per distinct type in sorted order, with original node order retained within each group.
- **Generic mapping tests:** use types outside the current C# vocabulary, including whitespace or punctuation supported by dynamic labels, and assert exact parameter and property values without normalization or fallback labels.
- **Failure tests:** make the fake transaction raise the same Neo4j client/query exception class used by the writer; assert the writer-specific error identifies the current type, chains the original exception, and does not continue to later groups or relationship creation.
- **Integration label tests:** query `labels(entity)` after rebuild and assert exact single-label sets, absence of `Entity` and `GraphNode`, preserved `type` properties, and generic unlabeled node counts.
- **Integration relationship tests:** retain assertions for native `CALLS`, absence of `RELATES_TO`, and preserved relationship `type` and custom properties after unlabeled endpoint matching.
- **Integration rebuild tests:** rebuild the same graph twice without duplicates, then rebuild a different graph and verify stale nodes and relationships are removed. Where a stable rejected label exists, seed a known graph, attempt the failing rebuild, and verify the known graph remains intact to prove rollback.
- **Regression tests:** run existing contract, serialization, CLI, .NET ingestion, and fixture tests unchanged; no format or generated JSON updates are expected.

Recommended commands:

```bash
cd graph-rag
pytest -m 'not integration'
docker compose up -d
pytest -m integration
docker compose down --volumes
```

## Questions

- None.