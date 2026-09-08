# ADR012 — Use source files for exact implementation detail

Status: Accepted

## Context

The graph is derived from the project and may omit implementation detail that is available in the source repository.

## Decision

The source repository remains authoritative, and agents read source files directly when exact implementation behavior is required.
