---
name: sally-retrieve-project-knowledge
description: Retrieve targeted project knowledge from Sally's local Neo4j Graph RAG using read-only Cypher. Use when an agent needs to understand project structure, locate relevant graph nodes, inspect relationships, dependencies, containment, callers/callees, inheritance, type usage, or documentation relationships before broader source-code investigation. Query the unified graph generically regardless of source technology or ingestion pipeline.
---

# Sally Retrieve Project Knowledge

Retrieve targeted project context directly from the local Neo4j Graph RAG.

The graph is derived project knowledge. The source repository remains the source of truth.

## Workflow

1. Identify the specific project question that needs graph context.

2. Start from known context.
  - If the task already identifies a relevant file or path, read it directly.
  - Use Graph RAG when relationships, dependencies, locations, surrounding structure, or cross-source context would help.
  - Do not replace a direct file read with a graph query when the exact file is already known.

3. Locate the Graph RAG compose.yaml in the Sally repository.
  - Use the Neo4j service defined by that Compose configuration.
  - Prefer executing cypher-shell inside the running Neo4j container through Docker Compose rather than constructing a separate host connection.
  - Read the connection credentials and database name from the existing Graph RAG configuration. Do not invent or assume credentials.
  - If the Neo4j Compose service is not running or the required connection information cannot be determined, report that Graph RAG is unavailable and continue with targeted source-code investigation. Do not start or rebuild Neo4j automatically.

4. Query Neo4j directly with targeted, read-only Cypher using an available `cypher-shell`. Prefer the `cypher-shell` available in the running Neo4j container when one is already running. Do not start, stop, rebuild, or ingest the graph as part of retrieval.

5. If the graph vocabulary or available properties are not yet known, discover them before formulating the substantive query. Keep discovery generic. Do not assume a language-specific or source-specific schema.

6. Query only the context needed to answer the current technical question. Prefer small, bounded result sets and focused traversals over broad graph dumps.

7. Use returned source locations and identifiers to inspect the corresponding source files directly when implementation detail is needed or when the graph answer is incomplete.

8. If the graph is unavailable, stale, or insufficient for the question, state that clearly and continue with targeted project investigation rather than inventing graph knowledge.

## Read-only requirement

Use only read-only Cypher operations for project knowledge retrieval.

Allowed operations include query clauses such as `MATCH`, `OPTIONAL MATCH`, `WHERE`, `WITH`, `UNWIND`, `RETURN`, `ORDER BY`, and `LIMIT`, plus read-only metadata procedures needed to understand the graph.

Never execute Cypher that creates, updates, deletes, imports, migrates, or otherwise modifies graph data or schema. In particular, do not use `CREATE`, `MERGE`, `SET`, `DELETE`, `DETACH DELETE`, `REMOVE`, `DROP`, `LOAD CSV`, or write procedures.

Do not trigger ingestion or a rebuild from this skill.

## Generic graph discovery

Discover graph structure only when needed. Useful read-only queries include:

```cypher
CALL db.labels()
```

```cypher
CALL db.relationshipTypes()
```

```cypher
MATCH (n)
UNWIND keys(n) AS key
RETURN DISTINCT key
ORDER BY key
```

Use discovered labels, relationship types, and properties to formulate the smallest useful query.

Do not maintain or assume a fixed vocabulary in this skill. Backend code, frontend code, documentation, and future ingestion sources share the same graph and must be queried through the same Neo4j entry point.

## Query guidance

Formulate Cypher from the technical subject being investigated, not from the user's full prompt verbatim.

Prefer exact matching when a stable identifier is known. Use broader matching only when discovery is necessary.

When locating a node without knowing which property identifies it, inspect available properties first or use a bounded generic property search rather than assuming a particular source technology.

When relationships matter, return enough information to understand both endpoints, the relationship direction and type, and relevant properties. Preserve useful graph identifiers such as `source_id` and source-location properties in results when present.

Keep variable-length traversals tightly bounded. Do not traverse the whole graph unless the task explicitly requires it.

Always apply a reasonable `LIMIT` to exploratory queries.

## Result use

Treat Neo4j results as project context, not as the final source of truth.

Use the graph to answer questions such as where relevant concepts live, what they connect to, and which source areas deserve inspection. For exact implementation behavior, verify against the source files identified by the graph when appropriate.

Do not expose Cypher or Neo4j details in Sally lifecycle artifacts unless those details are themselves relevant to the backlog item or implementation plan.

