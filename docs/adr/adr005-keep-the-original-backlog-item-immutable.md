# ADR005 — Keep the original backlog item immutable

Status: Accepted

## Context

The external backlog item belongs to the source system and should remain an authoritative record of the original request.

## Decision

Sally treats the source backlog item as read-only and produces a separate refined backlog item.
