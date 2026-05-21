# Design Risk Tiers

Tier from the request is a guess; tier after context scan is the decision.

## Tier 0 — Mechanical or purely local

Examples:

- Formatting.
- Copy/text changes.
- Isolated test edits.
- Small local bug fix.
- Local UI tweak.
- Mechanical migration where design is already decided.

Required behavior:

- Implement directly.
- No visible design note.
- No maintainability check unless a concern appears.

## Tier 1 — Local but maintainability-relevant

Examples:

- Small helper extraction.
- Local refactor.
- Local error handling.
- Minor duplication decision.
- Comment cleanup around non-obvious behavior.

Required behavior:

- Implement directly.
- Run a lightweight maintainability check at the end if code changed.

## Tier 2 — Design-impacting but reversible

Examples:

- Shared helper.
- Internal abstraction.
- Behavior used by multiple callers.
- Reused validation.
- Internal module boundary.
- New option/mode with limited scope.
- Duplicated domain logic that may need consolidation.

Required behavior:

- Inspect bounded context.
- Provide compact design note.
- Proceed unless the user asked for approval mode.
- Finish with maintainability check.

## Tier 3 — Expensive to undo

Examples:

- Public API or CLI contract.
- Schema or persistence model.
- Auth/security/permissions.
- Cross-cutting policy.
- Major module boundary.
- Shared data model.
- Behavior with broad caller impact.

Required behavior:

- Inspect broader context.
- Provide full design pass.
- Pause for approval before implementation.
- Finish with maintainability check after implementation.

## Context scan depth

Tier 0/1:

- Direct file plus obvious nearby pattern.

Tier 2:

- Direct file, callers/callees, related tests, and existing abstraction patterns.

Tier 3:

- Above, plus public contracts, schemas, architecture notes, and approval before coding.

Inspect enough context to avoid inventing design, but stop before research becomes ceremony.
