# ADR037 — Persist semantic node types as native Neo4j labels

Status: Accepted

## Context

A generic infrastructure label makes Neo4j visualization and exploration less useful and hides the semantic type of a node.

## Decision

Each node is persisted with its semantic type as its native Neo4j label, without adding a common infrastructure label such as `Entity` or `GraphNode`.
