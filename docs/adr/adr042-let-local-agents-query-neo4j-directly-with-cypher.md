# ADR042 — Let local agents query Neo4j directly with Cypher

Status: Accepted

## Context

A dedicated retrieval API or predefined query layer would add another abstraction, contract, and service boundary before stable retrieval patterns have emerged.

## Decision

For the local version of Sally, agents retrieve project knowledge by issuing small, targeted, read-only Cypher queries directly to Neo4j.

Do not introduce a retrieval API or fixed catalogue of query operations until concrete usage patterns justify one.
