---
name: sally-create-github-pull-request
description: Create a GitHub pull request for an approved Sally implementation.
---

# Create GitHub Pull Request

Create the pull request only after explicit approval from the Software Engineer.

Identify the backlog item associated with the implementation and its backlog item key.

Create the branch using:

`sally-<backlog-item-key>`

For example:

`sally-github-000001`

Include the approved Sally lifecycle artifacts associated with the backlog item in the pull request.

Include, when present:

- `.sally/<backlog-item-key>/refined-backlog-item.md`
- `.sally/<backlog-item-key>/implementation-plan.md`

Treat these artifacts as part of the implementation even if they are currently untracked.

Before committing, inspect the working tree and include only changes related to the approved implementation, including its Sally lifecycle artifacts. Do not include unrelated changes.

Use a concise imperative description of the implementation for both the commit message and pull request title.

Run or verify the relevant tests and checks before creating the pull request.

Use the [pull request template](../../../templates/pull-request.md) for the pull request body.

Describe the implemented change and relevant validation based on the actual implementation. Do not claim tests or checks that were not performed.

Reference the original GitHub issue using:

`Closes #<issue-number>`

Create the branch, commit the intended changes, push the branch, and create the pull request using the available GitHub tools.

Report the pull request URL and any relevant local working-tree changes that were deliberately excluded.

