# ADR021 — Use source-specific ingestion pipelines

Status: Accepted

## Context

Different source types require different parsers and semantic-analysis tools to extract reliable structure.

## Decision

Each source type has its own ingestion pipeline using tooling appropriate to that source, such as Roslyn for .NET and the TypeScript compiler API for TypeScript.
