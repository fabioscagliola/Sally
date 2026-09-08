# ADR036 — Support containerized ingestion without requiring host toolchains

Status: Accepted

## Context

Source-specific ingestion pipelines may depend on compilers, parsers, runtimes, SDKs, or other tooling that should not have to be installed on the host machine.

## Decision

Sally supports running ingestion pipelines in containers with the required source-specific toolchain bundled inside. The target project is mounted into the container and analyzed in its real repository context.

This approach applies across source technologies such as .NET, TypeScript, and future ingestion pipelines.
