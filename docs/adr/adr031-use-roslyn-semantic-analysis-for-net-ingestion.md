# ADR031 — Use Roslyn semantic analysis for .NET ingestion

Status: Accepted

## Context

Textual parsing of C# cannot reliably resolve declarations, calls, inheritance, implementations, or type relationships.

## Decision

The .NET ingestion pipeline uses Roslyn semantic analysis rather than textual parsing.
