# ADR032 — Use a compact semantic vocabulary for .NET declarations

Status: Accepted

## Context

Modeling every C# compiler symbol would create a large graph with more detail than the initial Sally use cases require.

## Decision

The .NET graph models `Project`, `Type`, `Method`, and `Property` as its primary declaration entities, with subtype distinctions represented through properties where appropriate.
