---
name: do-feature-plan-lite
description: Research and create a lightweight implementation plan for a feature
argument-hint: [feature-description]
---

# Planning: Feature Implementation Plan (Lite)

## Feature Description

$ARGUMENTS

## Determine Feature Name

Based on the feature description above, create a concise kebab-case feature name (e.g., "user-authentication", "payment-processing", "data-export").

**Feature Name**: [create-feature-name]

This will be used for the plan filename: `.agent-config/user/artifacts/plans/[3-digit-incrementing-number]-[feature-name].md`

## Lite Planning Guardrails

- Keep the plan compact (aim for 1-2 pages).
- Skip external research unless it is required to decide an approach.
- Focus on the minimum viable path; avoid speculative future-proofing.
- Limit the plan to 3-6 tasks with only necessary validation commands.
- **Don't Repeat the Obvious**: If a function signature, type hint, or field name is self-documenting, do not mandate additional prose. Reserve detailed documentation guidance for non-obvious behavior and edge cases.

## Quick Research Process

### 1. Identify Relevant Codebase Patterns

Search for the closest existing feature or component:
- Note relevant files and their structure
- Capture conventions and patterns to mirror
- Reuse existing utilities where possible

### 2. Confirm Scope and Approach

Determine:
- Which files need to be created or modified
- How the change integrates with existing code
- The minimum tests or validation required
- Demo impact per demo policy in `AGENTS.md`:
  - Demo guide updates for user-facing changes
  - Demo infra updates only for universal prerequisites (keep infra feature-agnostic)

### 3. Break Down Into Tasks

Create actionable tasks with:
- Specific file paths
- Exact function/class names
- Validation commands

## Output: Create Plan Document

Save plan as: `.agent-config/user/artifacts/plans/[3-digit-incrementing-number]-[feature-name].md` (using the feature name you created above)

**CRITICAL**: Format this plan for another agent to execute without seeing this conversation. Your saved plan must follow the structure in the template Read the output template at `references/output-template.md` and use it as the format for your output

## Quality Criteria

- [ ] Scope stays minimal and avoids speculative future work
- [ ] Tasks are ordered and independently testable
- [ ] Pattern references include file:line
- [ ] Validation commands are executable and minimal
- [ ] Acceptance criteria are measurable

## Confirmation

After creating the plan, confirm:
- ✅ Feature name created: [feature-name]
- ✅ Plan saved to `.agent-config/user/artifacts/plans/[3-digit-incrementing-number]-[feature-name].md`
- ✅ All tasks are explicit with file paths
- ✅ Validation commands are exact
- ✅ Another agent could execute this without context

**Next step**: Run `/do-plan-execution .agent-config/user/artifacts/plans/[the-name-you-created-earlier].md` to implement this feature
