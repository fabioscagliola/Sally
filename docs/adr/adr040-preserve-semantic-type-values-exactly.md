# ADR040 — Preserve semantic type values exactly

Status: Accepted

## Context

Changing semantic type names during persistence would create a hidden mapping between the graph contract and Neo4j.

## Decision

Semantic type values are persisted without sanitizing, renaming, prefixing, or suffixing them.
