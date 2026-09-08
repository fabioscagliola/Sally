# ADR013 — Fall back to targeted codebase search

Status: Accepted

## Context

Graph RAG may be unavailable, incomplete, or unable to resolve fuzzy or incorrectly named concepts.

## Decision

Agents use deliberate, targeted source search when Graph RAG is unavailable or insufficient, then use the discovered context as needed.
