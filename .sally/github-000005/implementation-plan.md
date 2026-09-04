# Implementation plan

Refined backlog item: [.sally/github-000005/refined-backlog-item.md](.sally/github-000005/refined-backlog-item.md)

## Affected components

- `graph-rag/src/graph_rag/writer.py`
  - Replace hard-coded `RELATES_TO` persistence with semantic relationship types.
  - Add semantic node labels while retaining `Entity`.
  - Preserve all existing node and relationship properties.
- `graph-rag/tests/test_writer.py`
  - Update fake-driver assertions for dynamic labels and relationship types.
  - Add generic and unusual semantic-type coverage without requiring Neo4j.
- `graph-rag/tests/integration/test_neo4j.py`
  - Verify native labels, native relationship types, preserved properties, rebuild idempotence, stale-data removal, and generic `Entity` queries against Neo4j 5.
- `graph-rag/fixtures/sample-graph.json`
  - Keep the version-1 JSON shape unchanged while ensuring the fixture exercises representative semantic node and relationship types.
- `graph-rag/README.md`
  - Document the native Neo4j mapping and retain the unchanged version-1 JSON boundary description.

## Implementation approach

Keep `GraphDocument`, its validation rules, and JSON serialization untouched. Change only the Neo4j writer's persistence mapping.

Use Neo4j 5 dynamic label and relationship-type expressions so semantic values remain data-driven rather than being interpolated into Cypher source. The preferred Cypher shape is equivalent to:

```cypher
MERGE (entity:Entity {source_id: node.source_id})
SET entity:$(node.type)
```

and:

```cypher
MERGE (source)-[edge:$(relationship.type) {type: relationship.type}]->(target)
```

Pass semantic values as query parameters. This avoids hard-coding the current vocabulary and avoids injection-prone string concatenation. The implementation must verify the syntax against the repository's Neo4j 5 Compose image. If any required dynamic-token operation cannot represent a non-empty contract-valid value, raise a clear persistence error and leave the original `type` property unchanged; never sanitize, normalize, rename, or silently fall back to `RELATES_TO`.

Retain the existing `Entity` label, `source_id` merge identity, delete-and-rebuild transaction, generic property assignment, and relationship properties. Do not add semantic indexes or constraints. Preserve the current transaction boundary so a failed rebuild rolls back through the Neo4j driver's managed transaction.

## Implementation steps

1. Confirm the exact dynamic label and relationship-type syntax supported by the pinned `neo4j:5-community` Compose image and the Python driver/server combination.
2. Add small writer helpers or query fragments for the dynamic semantic label and relationship type, keeping Cypher identifiers fixed and semantic values parameterized.
3. Update node persistence to merge nodes with `Entity`, apply the semantic node label, retain `entity.type`, source-location fields, and arbitrary validated node properties.
4. Update relationship persistence to use the semantic relationship type, retain `edge.type`, and apply arbitrary validated relationship properties. Remove all reliance on `RELATES_TO` for newly written relationships.
5. Preserve the existing `DETACH DELETE`, `MERGE`, and transaction behavior. Do not add indexes or constraints.
6. Update unit-test fakes and assertions to inspect dynamic-token query structure and semantic values, including a type containing characters that require Neo4j token handling. Verify the original type value is passed unchanged.
7. Update the sample fixture and documentation only as needed to show the native mapping; do not change the version-1 format or serialized field names.
8. Update the Neo4j integration suite to query native semantic labels and relationship types, verify `Entity` remains present, verify `RELATES_TO` is absent, repeat rebuilds, and verify stale graph data is removed.
9. Start the disposable Compose Neo4j instance and run the focused integration suite against it. Run the complete non-integration test suite afterward.

## Tests

- **Writer unit tests:** verify the first transaction operation still deletes the graph, node writes retain `Entity`, node semantic types are supplied for dynamic labels, relationship semantic types are supplied for dynamic relationship types, and original `type` values remain unchanged.
- **Generic mapping tests:** use semantic values not named in the current C# vocabulary to prove the writer does not branch on a hard-coded list. Include values with punctuation or whitespace where Neo4j 5 permits them, and assert that the writer passes the exact original strings.
- **Invalid persistence tests:** verify a database/query failure is surfaced as a clear exception and that no fallback to `RELATES_TO` or renamed semantic value occurs.
- **Integration label tests:** write nodes with different semantic types and query `MATCH (entity:Entity:Method)` and other native labels, confirming the common `Entity` label and semantic labels coexist and the `type` property is preserved.
- **Integration relationship tests:** write semantic relationships and query each native relationship type, confirming relationship `type` properties and custom properties are preserved and no `RELATES_TO` relationships are created.
- **Integration rebuild tests:** rebuild the same document twice and verify node/relationship counts and identities do not duplicate; rebuild a different document and verify stale entities and relationships are removed.
- **Contract regression tests:** run the existing contract and serialization tests unchanged to prove the technology-independent representation and JSON serialization remain stable.

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