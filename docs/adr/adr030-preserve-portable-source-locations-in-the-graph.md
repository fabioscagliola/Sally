# ADR030 — Preserve portable source locations in the graph

Status: Accepted

## Context

Graph results must be able to direct an agent back to authoritative source without depending on machine-specific absolute paths.

## Decision

Graph nodes preserve repository-relative source locations and source positions where available.
