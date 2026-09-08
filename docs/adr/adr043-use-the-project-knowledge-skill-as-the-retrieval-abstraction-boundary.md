# ADR043 — Use the project knowledge skill as the retrieval abstraction boundary

Status: Accepted

## Context

Lifecycle agents should not contain Neo4j-specific connection, schema-discovery, or query guidance.

## Decision

Neo4j retrieval behavior is encapsulated in the `sally-retrieve-project-knowledge` skill rather than duplicated in Refiner, Planner, or Coder.
