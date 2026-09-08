# ADR038 — Persist semantic relationship types as native Neo4j relationship types

Status: Accepted

## Context

Generic relationship types obscure the meaning of graph connections and make Cypher queries less natural.

## Decision

Each relationship is persisted using its semantic type as the native Neo4j relationship type.
