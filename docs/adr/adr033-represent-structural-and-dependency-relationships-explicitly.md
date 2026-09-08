# ADR033 — Represent structural and dependency relationships explicitly

Status: Accepted

## Context

Agents need relationships between semantic entities, not only isolated declarations.

## Decision

The .NET ingestion pipeline emits explicit relationships including `CONTAINS`, `INHERITS`, `IMPLEMENTS`, `CALLS`, and `USES_TYPE`.
