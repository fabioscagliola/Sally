# ADR029 — Use stable source-derived graph identifiers

Status: Accepted

## Context

A complete rebuild should produce recognizable identities for the same source declarations so relationships remain deterministic and inspectable.

## Decision

Graph node identifiers are derived deterministically from stable project and source identities.
