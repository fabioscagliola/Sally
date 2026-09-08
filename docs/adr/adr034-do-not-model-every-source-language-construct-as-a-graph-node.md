# ADR034 — Do not model every source-language construct as a graph node

Status: Accepted

## Context

Parameters, locals, namespaces, files, external framework symbols, and similar compiler details can greatly increase graph size without proportionate retrieval value.

## Decision

The initial .NET graph omits low-value source-language constructs unless a concrete retrieval requirement justifies adding them.
