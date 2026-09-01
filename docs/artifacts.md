# Artifacts

Sally stores its lifecycle artifacts in the target repository under:

`.sally/<backlog-item-key>/`

The key identifies the source system and the original backlog item, for example:

- `github-000023`
- `gitlab-000075`

Numeric identifiers are zero-padded to six digits.

The following artifacts are currently supported:

- `.sally/<backlog-item-key>/refined-backlog-item.md`
- `.sally/<backlog-item-key>/implementation-plan.md`

