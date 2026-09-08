# ADR035 — Resolve internal types through external generic wrappers

Status: Accepted

## Context

Internal project types often appear inside framework or library wrappers such as `List<Block>` or `DbSet<Person>`.

## Decision

The .NET ingestion pipeline recursively resolves type arguments so internal project types are represented by `USES_TYPE` relationships even when wrapped by external generic types.
