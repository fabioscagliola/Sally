# ADR028 — Use generic semantic node and relationship types

Status: Accepted

## Context

The common graph representation must support future source types without requiring its core contract to know every possible semantic vocabulary.

## Decision

Ingestion producers supply semantic node and relationship types without requiring the common graph layer to maintain a closed vocabulary.
