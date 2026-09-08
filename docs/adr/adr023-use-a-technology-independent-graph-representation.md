# ADR023 — Use a technology-independent graph representation

Status: Accepted

## Context

Multiple ingestion pipelines need a common boundary that can evolve independently from both source-language tooling and graph persistence.

## Decision

Sally uses a strict, versioned, technology-independent graph representation for semantic nodes, relationships, properties, and source locations.
