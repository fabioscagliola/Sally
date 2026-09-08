# ADR044 — Keep project knowledge queries read-only

Status: Accepted

## Context

Lifecycle agents need to inspect project knowledge but should not be able to mutate, rebuild, or ingest the graph while performing delivery work.

## Decision

The project-knowledge retrieval capability permits read-only graph inspection and prohibits graph mutation.
