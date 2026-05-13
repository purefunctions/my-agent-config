# Feature Implementation Plan (Lite)

## Feature: [Feature Name]

## Feature Description

[1 paragraph description of what this feature does and what problem it solves. Be specific about user-facing behavior and system impact]

## User Story

As a [specific type of user]
I want to [specific action/goal]
So that [specific benefit/value]

## Problem Statement

[1 short paragraph clearly defining the specific problem or opportunity that this feature solves]

## Solution Statement

[1-2 paragraphs describing the technical approach, key decisions, and how this integrates with existing architecture]

**Constraints & Assumptions:**
- [Constraint or assumption 1]
- [Constraint or assumption 2]

## Feature Metadata

**Feature Type**: [New Capability/Enhancement/Refactor/Bug Fix]
**Estimated Complexity**: [Low/Medium/High]
**Primary Systems Affected**: [List of main components/services]
**Dependencies**: [External libraries or services required]

---

## Relevant Files (Must Read)

The executing agent MUST read these files to understand patterns and conventions.

### Core Files
- `AGENTS.md`, `CLAUDE.md` or similar - Project principles, logging rules, testing requirements (Section 6.1), docstring style (Section 4.3 graduated examples)
- `[file-path]` (lines X-Y) - [why relevant]

### Similar Patterns
- `[file-path]` (lines X-Y) - [example of pattern to follow]

### Integration Points (Must Update)
- `[file-path]` (lines X-Y) - [where to register routes, handlers, or services]

---

## Implementation Plan

[Brief outline of the work.]

- Update or add [schemas/types/models]
- Implement [core logic]
- Wire into [entry point]
- Add tests or validation

---

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom. Each task is atomic and independently testable.

### Task Format Guidelines

- **CREATE**: New files or components
- **UPDATE**: Modify existing files
- **ADD**: Insert new functionality into existing code
- **REMOVE**: Delete deprecated code
- **REFACTOR**: Restructure without changing behavior
- **MIRROR**: Copy pattern from elsewhere in codebase

Each task must include file-scoped validation commands; full-suite validation belongs in Validation Commands.

### Task 1: [Task Name]
**File**: `[exact/path/to/file.py]` (create new OR modify existing)

- **IMPLEMENT**: [Specific implementation detail]
- **PATTERN**: [Reference to existing pattern - file:line]
- **IMPORTS**: [Required imports and dependencies]
- **PITFALL**: [Known issue or constraint to avoid]
- **VALIDATION**:
  - `uv run ruff format [file]`
  - `uv run ruff check [file]` passes
  - `uv run pyright [file]` passes

---

If additional implementation steps are needed, repeat the Task 1 block with a new task name and file path.

---

### Task 2: [Testing Task Name]
**File**: `tests/[path]/test_[module].py` (create new OR modify existing)

- **IMPLEMENT**: Comprehensive unit tests covering all new models, happy paths, and error cases (do not limit tests to only the happy path).
- **TEST ORGANIZATION**: Follow `AGENTS.md` Section 6.1 - consolidate related assertions into single test methods; use `@pytest.mark.parametrize` for input variations
- **PATTERN**: [Reference to existing test pattern - file:line]
- **PITFALL**: [Known issue or constraint to avoid]
- **VALIDATION**:
  - `uv run ruff format [file]`
  - `uv run ruff check [file]` passes
  - `uv run pytest tests/[path] -v` passes

---

## Validation Commands

Execute these commands to validate success:

# Linting (MUST pass with 0 errors)
uv run ruff check src/

# Type checking (if applicable)
uv run pyright src/

# Tests (MUST pass)
uv run pytest tests/ -v

**Success definition**: All commands complete with exit code 0, all tests pass, no errors or warnings.

---

## Acceptance Criteria

This feature is complete when:

- [ ] Feature works as described in User Story
- [ ] All validation commands pass
- [ ] No regressions in existing features
- [ ] Documentation updated (if applicable)
- [ ] Demo impact assessed and updated (demo policy in `AGENTS.md`)

---

## Demo & Manual Validation

Required for user-facing changes.

**Demo infra updates (feature-agnostic):** (Yes/No). If Yes: list files under `demo/` and why they are universal prerequisites.

**Demo guide updates (feature-specific):**
- Guide path(s): `demo/guides/[NN]-[feature].md`
- Copy/paste commands (3-8 lines) to validate end-to-end.

---

## Checklist Before Starting Implementation

The executing agent should verify:
- [ ] Read all files in "Relevant Files" section
- [ ] Understood the solution approach
- [ ] Clear on step-by-step task order
- [ ] Validation commands are executable in this environment

If any checklist item is unclear, ask for clarification before starting.

---

## Notes

[Additional context, tradeoffs, or limitations]
