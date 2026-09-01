# Refine a GitHub backlog item

This document describes how to use GitHub Copilot in Visual Studio Code and the GitHub MCP Server to run Sally Refiner against a GitHub issue.

## Prerequisites

- Visual Studio Code
- GitHub Copilot
- GitHub MCP Server
- A local checkout of Sally
- A local checkout of the target project

## Set up the workspace

Open the Sally repository in Visual Studio Code.

Add the target project to the same workspace using **File** > **Add Folder to Workspace...**

## Install the GitHub MCP Server

Install the [GitHub MCP Server](https://github.com/github/github-mcp-server) extension.

## Verify Sally

In Copilot, verify that

- `Sally Refiner` is available as a custom agent
- `retrieve-github-issue` is available as a skill

## Run the Refiner

Select the `Sally Refiner` agent.

Use a prompt like the following.

```
Refine this backlog item:
https://github.com/fabioscagliola/NerdyWeirdWords/issues/11
Target project: NerdyWeirdWords
```

## Output

The refined backlog item is written as a Markdown file in the target repository at the location defined in the [Artifacts](../artifacts.md) document.

