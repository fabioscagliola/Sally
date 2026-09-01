# Lifecycle

Sally supports the journey from backlog item to pull request through a lifecycle with three AI-augmented stages.

1. Backlog
2. Refinement
3. Implementation plan
4. Coding
5. Pull request

The Software Engineer remains in control throughout the lifecycle, reviewing and interacting with each agent before approving its output and moving to the next stage.

![Lifecycle](/assets/lifecycle.jpg)

## 1. Backlog

The starting point of the Sally lifecycle is a GitHub issue, created for example by a Business Analyst, describing the business needs and requirements.

## 2. Refinement

The Sally Refiner agent retrieves the GitHub issue and refines it.

The agent helps identify missing information, assumptions, ambiguities, and define acceptance criteria.

The Software Engineer reviews the refined backlog item and interacts with the agent until satisfied with the result.

Output: Refined Backlog Item

## 3. Implementation plan

The Sally Planner agent reads the approved refined backlog item and investigates how to implement it.

The agent analyzes the available project context, including the codebase, and produces an implementation plan.

The Software Engineer reviews the plan and interacts with the agent until satisfied with the result.

Output: Implementation Plan

## 4. Coding

The Sally Coder agent reads the approved implementation plan and implements it.

The agent creates or modifies the necessary code and tests.

The Software Engineer reviews the implementation and interacts with the agent until satisfied with the result.

Output: Code & Tests

## 5. Pull request

Once the implementation is approved, the Sally Coder agent creates a pull request containing the completed changes.

