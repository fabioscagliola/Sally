# ADR045 — Discover graph vocabulary instead of hard-coding it in the skill

Status: Accepted

## Context

The graph vocabulary will expand as new source-specific ingestion pipelines are introduced.

## Decision

The project-knowledge skill discovers available labels, relationship types, and relevant properties instead of maintaining a hard-coded language-specific vocabulary.
