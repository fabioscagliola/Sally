# ADR027 — Use full delete-and-rebuild ingestion in version 1

Status: Accepted

## Context

Incremental graph synchronization introduces identity, deletion, ordering, and consistency complexity before those requirements have been demonstrated.

## Decision

Version 1 ingestion clears and rebuilds the graph completely rather than updating it incrementally.
