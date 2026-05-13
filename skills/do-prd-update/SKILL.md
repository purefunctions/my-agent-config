---
name: do-prd-update
description: Update PRD status and archive completed/superseded specs
argument-hint: feature-id or ids and change-type e.g. "1.2 complete" or "1.2.1 supersede"
allowed-tools: Read, Edit
---

# PRD Update: Keep Active PRD Small

Keep `.agent-config/user/artifacts/PRD.md` concise and keep completed specs in `.agent-config/user/artifacts/prd-archive.md`.

Use this command when:
- A feature is completed and PRD needs a status update + archive entry.
- A feature spec is superseded and should be archived.
- PRD has grown too large for context and needs pruning.

Do not use this command for routine code changes.

## Inputs (ask only if missing)

- Feature ID(s): e.g. `1.2`, `1.2.1`
- Change type: `complete` | `supersede` | `prune`
- One-line summary (for the Completed table)
- Links (optional but preferred): plan doc(s), PR URL(s), commit SHA(s)

## Invariants

- `.agent-config/user/artifacts/PRD.md` remains the active, context-loaded requirements document.
- Completed/superseded feature specs live in `.agent-config/user/artifacts/prd-archive.md`.
- The archive is append-only except for small typo fixes.
- Avoid large rewrites/reformatting; keep diffs minimal and reviewable.

## Procedure

### 1) Identify the feature section(s)

- Locate the feature section(s) in `.agent-config/user/artifacts/PRD.md`.
- Determine whether the full spec currently lives in `.agent-config/user/artifacts/PRD.md` or is already archived.

### 2) Update the Completed Features table (active PRD)

- In `.agent-config/user/artifacts/PRD.md`, update `### Completed Features (One-Line Summary)`.
- If the feature is newly completed:
  - Add a row with `Feature`, `Summary`, and `Implementation`.
  - Use `Implemented` (or `Implemented (wiring deferred to X.Y.Z)` when applicable).
- If the feature is superseded:
  - Keep the old row but mark `Implementation` as `Superseded (see archive)`.

### 3) Archive the full feature spec

If the spec is currently in `.agent-config/user/artifacts/PRD.md`:
- Copy the entire feature section into `.agent-config/user/artifacts/prd-archive.md` under `## Completed Features`.
- Preserve headings and tables as-is.
- Do not change numbering; keep the original feature ID.

If the spec is already archived:
- Add a short note in `.agent-config/user/artifacts/prd-archive.md` documenting what changed and why.

### 4) Replace the active PRD section with an archive pointer

- In `.agent-config/user/artifacts/PRD.md`, replace the detailed feature section with a short stub:

```md
### 10.X Feature <ID>: <Name>

Archived in `.agent-config/user/artifacts/prd-archive.md`.
```

- Keep the heading in place so feature numbering remains stable.

### 5) Keep cross-references current

- If you add a new file (archive or new plan doc), ensure links in `.agent-config/user/artifacts/PRD.md` remain correct.
- If the PRD references feature status (Planned/Completed), update it.

### 6) Verification

- Ensure `.agent-config/user/artifacts/PRD.md` still reads cleanly end-to-end.
- Ensure `.agent-config/user/artifacts/prd-archive.md` contains the complete spec and is not duplicated.
- Run markdown sanity check by eyeballing headings and tables; no tooling required.

## Output format

Return:
- Files changed (paths)
- Feature rows added/updated
- Archive entries added
- Any follow-ups (if the PRD and implementation disagree)
