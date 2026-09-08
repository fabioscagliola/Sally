# ADR041 — Do not create indexes or constraints per semantic type initially

Status: Accepted

## Context

The semantic vocabulary is intentionally open-ended and will expand as new ingestion sources are added.

## Decision

The initial Neo4j persistence layer does not create indexes or constraints for every semantic label or relationship type.
