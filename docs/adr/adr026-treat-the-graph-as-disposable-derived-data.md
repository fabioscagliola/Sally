# ADR026 — Treat the graph as disposable derived data

Status: Accepted

## Context

The graph is generated from authoritative project sources and can become stale after those sources change.

## Decision

The repository and source documents remain authoritative; the Neo4j graph is disposable derived data that can be rebuilt at any time.
