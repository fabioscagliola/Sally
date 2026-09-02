# GitHub quickstart guide

This guide explains how to get started using GitHub Copilot in Visual Studio Code to run the Sally lifecycle against a GitHub issue.

## Prerequisites

- Visual Studio Code
- GitHub Copilot
- GitHub MCP Server
- A local checkout of Sally
- A local checkout of the target project

## Install the GitHub MCP Server

Install the [GitHub MCP Server](https://github.com/github/github-mcp-server) Visual Studio Code extension.

## Set up the workspace

Open the Sally repository in Visual Studio Code.

Add the target project to the same workspace using **File** > **Add Folder to Workspace...**

## Verify Sally

In GitHub Copilot, verify that the following custom agents are available.

- Sally Refiner
- Sally Planner
- Sally Coder

And verify that the following custom skills are available.

- retrieve-github-issue

## Run the Refiner

Select the Sally Refiner agent.

Use a prompt like the following.

> Refine this backlog item:
>
> https://github.com/fabioscagliola/NerdyWeirdWords/issues/11
>
> Target project: NerdyWeirdWords

### Output

The refined backlog item is written as a Markdown file in the target repository at the location defined in the [Artifacts](../artifacts.md) document.

Review the refined backlog item and interact with Sally Refiner to resolve questions and improve it until you are satisfied with the result.

Explicitly approve the refined backlog item before moving to the next stage.

## Run the Planner

Select the Sally Planner agent.

Use a prompt like the following.

> Create an implementation plan for this approved refined backlog item:
>
> .sally/github-000011/refined-backlog-item.md
>
> Target project: NerdyWeirdWords

### Output

The implementation plan is written as a Markdown file in the target repository at the location defined in the [Artifacts](../artifacts.md) document.

Review the implementation plan and interact with Sally Planner to resolve questions and improve it until you are satisfied with the result.

Explicitly approve the implementation plan before moving to the next stage.

## Run the Coder

Select the Sally Coder agent.

Use a prompt like the following.

> Implement this approved implementation plan:
>
> .sally/github-000011/implementation-plan.md
>
> Target project: NerdyWeirdWords

### Output

Sally Coder creates or modifies the necessary code and tests, and runs the relevant tests and checks where possible.

Review the implementation and interact with Sally Coder to resolve issues and improve it until you are satisfied with the result.

Explicitly approve the implementation before creating the pull request.

## Create the pull request

With the Sally Coder agent still selected, use a prompt like the following.

> Approved. Create the pull request.

Sally Coder creates a branch and a commit, pushes the changes, and creates the pull request including code, tests, and the Sally artifacts.

