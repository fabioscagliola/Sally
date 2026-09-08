# ADR022 — Keep ingestion producers independent of Neo4j

Status: Accepted

## Context

Language-specific analyzers should not be coupled to a particular graph database or persistence technology.

## Decision

Ingestion producers emit the common graph representation and do not contain Neo4j-specific persistence logic.
