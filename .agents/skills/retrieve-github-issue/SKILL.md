---
name: retrieve-github-issue
description: Retrieve a GitHub issue to use as a backlog item. Use when an agent needs to read the original backlog item from a GitHub repository.
---

# Retrieve GitHub Issue

Retrieve the GitHub issue using the available GitHub tools.

Accept either:

- a GitHub issue URL; or
- an issue number when the repository can be determined from the target project.

Retrieve the issue title, body, URL, labels, and comments.

Treat the retrieved issue as read-only source material.

Do not modify, update, close, comment on, or otherwise change the GitHub issue.

Preserve the original content and provide it to the calling agent as the backlog item.

