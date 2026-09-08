# ADR009 — Use platform-specific skills for backlog-item retrieval and pull-request creation

Status: Accepted

## Context

Backlog and repository platforms expose different APIs and workflows for retrieving backlog items and creating pull requests or merge requests.

## Decision

Sally encapsulates platform-specific backlog-item retrieval and pull-request creation in dedicated skills. Lifecycle agents select the appropriate skill for the target platform.