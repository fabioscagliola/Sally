# ADR011 — Use Graph RAG as the structured project knowledge layer

Status: Accepted

## Context

Agents need structural and relational knowledge about the target project, including components, dependencies, containment, ownership, type usage, and cross-source relationships. Repeatedly searching the raw codebase for this information is inefficient and often obscures those relationships.

## Decision

Sally uses Graph RAG as its structured project knowledge layer. Agents use it when they need to discover project structure, affected components, relationships, dependencies, ownership, or cross-source context.
