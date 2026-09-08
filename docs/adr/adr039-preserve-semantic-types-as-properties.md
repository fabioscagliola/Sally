# ADR039 — Preserve semantic types as properties

Status: Accepted

## Context

The common graph representation carries semantic `type` values independently from the persistence technology.

## Decision

Neo4j retains the semantic `type` property even when the same value is also represented as a native label or relationship type.
