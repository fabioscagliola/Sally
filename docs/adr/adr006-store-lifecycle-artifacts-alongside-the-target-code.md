# ADR006 — Store lifecycle artifacts alongside the target code

Status: Accepted

## Context

Refined backlog items and implementation plans are part of the implementation context and should remain versioned with the code they describe.

## Decision

Sally stores its lifecycle artifacts under `.sally/<backlog-item-key>/` in the target repository.
