# Feature Implementation Plan

## Feature: [Feature Name]

## Feature Description

[2-3 paragraph description of what this feature does and what problem it solves. Be specific about system impact and user-facing behavior.]

## User Story

As a [specific type of user]
I want to [specific action/goal]
So that [specific benefit/value]

## Problem Statement

[1-2 paragraphs clearly defining the specific problem or opportunity that this feature solves. Include current pain or limitation, why existing solutions do not work, and impact of not solving this.]

## Solution Statement

[2-3 paragraphs describing: the technical approach, why we chose it versus alternatives, key technical decisions and tradeoffs, and how this integrates with existing architecture.]

**Approach Decision:**
We chose [approach name] because:
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Alternatives Considered:**
- [Alternative 1]: Rejected because [reason]
- [Alternative 2]: Rejected because [reason]

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

The executing agent MUST read these files to understand patterns and conventions. Include a brief reason for each file and cite file:line or file:section where possible.

### Core Files
- `AGENTS.md`, `CLAUDE.md` or similar - Project principles, logging rules, testing requirements (Section 6.1), docstring style (Section 4.3 graduated examples)
- `[file-path]` (lines X-Y or section name) - [why relevant, what to learn]
- `[file-path]` (lines X-Y or section name) - [why relevant]

### Similar Features (Examples to Follow)
- `[file-path]` (lines X-Y) - [example of similar pattern to follow]
- `[file-path]` (lines X-Y) - [specific pattern demonstrated]

### Integration Points (Must Update)
- `[file-path]` (lines X-Y) - [where to register routes, handlers, or services]
- `[file-path]` (lines X-Y) - [config or wiring changes]

### New Files to Create
- `path/to/new_service.py` - Service implementation for X functionality
- `path/to/new_model.py` - Data model for Y resource
- `tests/path/to/test_new_service.py` - Unit tests for new service

---

## Research Documentation (Must Read)

Use these resources for implementation guidance.

### Library Documentation
- [Library Name - Specific Feature](https://docs.example.com/path#anchor)
  - Section: [Specific section name]
  - Summary: [What to learn from this - 1-2 sentences]
  - Use for: [Which implementation step needs this]

### API References
- [API Name - Endpoint Docs](https://api.example.com/reference#endpoint)
  - Endpoint: [Specific endpoint details]
  - Parameters: [Key parameters to understand]
  - Use for: [Which implementation step needs this]

### Implementation Examples
- [Example Title](https://github.com/repo/file.py#L10-L50)
  - Pattern shown: [What pattern this demonstrates]
  - Adapt for: [How to adapt to our use case]

---

## Patterns to Follow

Include concrete examples from the codebase with file:line references. If this is a greenfield area, cite design docs or mark as N/A.

**Naming Conventions:** [file:line or section + short example]
**Error Handling:** [file:line or section + short example]
**Logging Pattern:** [file:line or section + short example]
**Other Relevant Patterns:** [file:line or section + short example]

---

## Implementation Plan

### Phase 1: Foundation
[What foundational work is needed first?]
- Schemas/types/classes/models to define
- Shared utilities to create
- Dependencies to add

### Phase 2: Core Implementation
[What is the main implementation work?]
- Core functionality to build
- Business logic to add
- Integration points to implement

### Phase 3: Integration
[How does this integrate with existing features?]
- Integration with existing features
- Configuration/registration updates
- Backward compatibility considerations

### Phase 4: Testing and Validation
[How will we test and validate?]
- Testing strategy
- Validation approach
- Manual checks if needed

---

## Step by Step Tasks

IMPORTANT: Execute every step in order, top to bottom. Each task is atomic and independently testable.

Standard per-file validation (reference in tasks):
- Run standard formatting check on `<file>` (see `AGENTS.md`)
- Run standard lint check on `<file>` (see `AGENTS.md`)
- Run standard type check on `<file>` (see `AGENTS.md`)

### Task Format Guidelines

Use information-dense action keywords for clarity:
- **CREATE**: New files or components
- **UPDATE**: Modify existing files
- **ADD**: Insert new functionality into existing code
- **REMOVE**: Delete deprecated code
- **REFACTOR**: Restructure without changing behavior
- **MIRROR**: Copy pattern from elsewhere in codebase
- **IMPLEMENT**: Allowed when none of the above fit cleanly (example: “Implement schema validation behavior”)

Each task must include file-scoped validation commands (may reference the standard per-file validation above). Code snippets are optional; use concise test descriptions when possible. The number of tasks is not limited; add as many as needed for clarity.

### Task 1: [Foundational Task Name]
**File**: `[exact/path/to/file.py]` (create new OR modify existing)

- **CREATE/UPDATE**: [Specific implementation detail]
- **PATTERN**: [Reference to existing pattern - file:line]
- **IMPORTS**: [Required imports and dependencies]
- **PITFALL**: [Known issue or constraint to avoid]
- **VALIDATION**:
  - Standard per-file validation

---

### Task 2: [Implementation Task Name]
**File**: `[exact/path/to/file.py]` (create new OR modify existing)

- **ADD/UPDATE**: [Specific function/class]
- **PATTERN**: [Reference to existing pattern - file:line]
- **IMPORTS**: [Required imports and dependencies]
- **PITFALL**: [Known issue or constraint to avoid]
- **VALIDATION**:
  - Standard per-file validation

---

### Task 3: [Testing Task Name]
**File**: `tests/[path]/test_[module].py` (create new)
**Scope**: [List classes/functions to test, e.g. "All public methods in module X"]

**Implementation Requirements**:
1. **Coverage**: Iterate through EVERY class/function in the scope.
2. **Positive Cases**: Verify expected behavior for valid inputs.
3. **Negative Cases**: Verify error handling for invalid inputs/states.
4. **Edge Cases & Logic Examples (Non-Exhaustive)**:
   - [Constraint 1]
   - [Constraint 2]

- **VALIDATION**:
  - Standard per-file validation
  - Run tests for `tests/[path]` (command from `AGENTS.md`)

---

### Task 4: [Integration Task Name]
**File**: `[exact/path/to/file.py]`

- **ADD/UPDATE**: [Register component or integration point]
- **PATTERN**: [Reference to existing pattern - file:line]
- **NOTE**: [Backward compatibility requirements, if any]
- **VALIDATION**:
  - Standard per-file validation
  - Feature accessible through [entry point]

---

### Task 5: Final Validation

Run all validation commands in order (mirror Validation Commands section).

---

## Testing Strategy

### Unit Tests
**Location**: `tests/[module]/test_[file].py`
**Mark with**: `[Unit test marker from AGENTS.md]`

**Test Organization**: Follow `AGENTS.md` testing guidelines.

**Scope Requirement**: Tests MUST cover all public methods, data models, and edge cases in the implementation, even if not explicitly listed below.

Test in isolation:
- [Component 1] - [what to test]
- [Component 2] - [what to test]
- **Verify ALL data models** (defaults, constraints, invalid inputs)
- **Verify ALL error paths** (e.g., file not found, permission denied)
- Each function's happy path
- Edge cases and error cases

### Integration Tests (if applicable)
**Location**: `tests/integration/test_[feature].py`
**Mark with**: `[Integration test marker from AGENTS.md]`

Test component interaction:
- [Integration point 1] - [what to test]
- [Integration point 2] - [what to test]
- End-to-end workflows
- External system interactions

### Edge Cases
Must test:
- [Edge case 1: Description] - [Expected behavior]
- [Edge case 2: Description] - [Expected behavior]
- Empty/null inputs - [Expected behavior]
- Maximum limits - [Expected behavior]

---

## Acceptance Criteria

This feature is complete when:
- [ ] [Specific criterion 1 - measurable]
- [ ] [Specific criterion 2 - measurable]
- [ ] All linters pass
- [ ] All tests pass (unit + integration)
- [ ] Feature works as described in User Story
- [ ] No regressions in existing features
- [ ] Documentation updated (if applicable)
- [ ] Logging includes structured context
- [ ] Demo impact assessed and updated (demo policy in `AGENTS.md`)

---

## Demo & Manual Validation

This section is REQUIRED for user-facing changes (CLI/SDK/API contracts) and for any feature that introduces new environment prerequisites.

**Demo Infrastructure Impact (keep feature-agnostic):**
- Infra updates required? (Yes/No)
- If Yes: list exact files to update under `demo/` (e.g., `demo/scripts/setup.sh`, `demo/docker-compose.yml`, `demo/.env.template`, `demo/data/seed.sql`) and explain why each change is a universal prerequisite.

**Demo Guide Impact (feature-specific):**
- New/updated guide(s) under `demo/guides/`:
  - `demo/guides/[NN]-[feature].md`
- Copy/paste manual validation commands (setup -> run service -> run CLI):
  - `demo/scripts/setup.sh`
  - `[Run Service Command]`
  - `[Run CLI Command]`
- Expected output notes:
  - What must match exactly (stable strings/contracts)
  - What can vary (timestamps, ids, paths)

---

## Validation Commands

Execute these exact commands to validate success (full-suite validation only; per-task validation lives in Step by Step Tasks):

- [Formatting Check Command from AGENTS.md]
- [Linting Check Command from AGENTS.md]
- [Type Checking Command from AGENTS.md]
- [Unit Test Command from AGENTS.md]
- [Integration Test Command from AGENTS.md] (if applicable)
- [Full Test Command from AGENTS.md]
- [Manual testing steps if needed]

**Success definition**: All commands complete with exit code 0, all tests pass, no errors or warnings.

---

## Notes

[Include any additional context such as:
- Future considerations or planned improvements
- Known limitations of this approach
- Deployment considerations
- Performance implications
- Security considerations
- Breaking change warnings]

---

## Checklist Before Starting Implementation

The executing agent should verify:
- [ ] Read all files in "Relevant Files" section
- [ ] Reviewed all research documentation
- [ ] Understood the solution approach and constraints
- [ ] Clear on step-by-step task order
- [ ] Validation commands are executable in this environment
- [ ] Ready to execute tasks in sequence

If any checklist item is unclear, ask for clarification before starting.
