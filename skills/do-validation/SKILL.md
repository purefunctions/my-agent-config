---
name: do-validation
description: Run comprehensive validation checks on the repository
argument-hint: (optional - none required)
allowed-tools: Bash(*)
---

# Validate: Run Repository Validation Suite

Run comprehensive validation checks on the repository including formatting, linting, type checking, and tests.

## Validation Steps

### 1. Check Code Formatting

Verify that code follows the project's formatting standards.

Run the formatting check command specified in **`AGENTS.md`** under the "Validation" or "Development" section.

### 2. Run Linting

Check for code quality issues and violations.

Run the linting command specified in **`AGENTS.md`**.

### 3. Type Checking

Validate type safety across the codebase.

Run the type checking command specified in **`AGENTS.md`**.

### 4. Run Tests

Execute the full test suite with verbose output.

Run the test command specified in **`AGENTS.md`**.

## Summary Report

Generate comprehensive validation report with the following sections:

### Tests Results
- Total tests executed
- Tests passed ✅
- Tests failed ❌
- Pass rate percentage

### Type Checking Status
- Result: ✅ PASS or ❌ FAIL
- Number of errors (if any)
- Number of warnings (if any)
- List warnings encountered

### Linting Status
- Result: ✅ PASS or ❌ FAIL
- Number of errors (if any)
- Number of warnings (if any)
- List warnings encountered

### Code Formatting Status
- Formatting check result: ✅ PASS or ❌ FAIL
- If formatting issues found, list them

### Overall Health Assessment
- **PASS**: All checks pass with no errors (warnings acceptable)
- **FAIL**: Any check fails or has errors

---

## Example Report Format

```
═══════════════════════════════════════════════════════════
  REPOSITORY VALIDATION REPORT
═══════════════════════════════════════════════════════════

📋 TEST RESULTS
  Total Tests Run: 247
  ✅ Passed: 247
  ❌ Failed: 0
  Pass Rate: 100%

🔍 TYPE CHECKING
  Status: ✅ PASS
  Errors: 0
  Warnings: 0

🧹 LINTING
  Status: ✅ PASS
  Errors: 0
  Warnings: 0

📝 CODE FORMATTING
  Status: ✅ PASS
  No formatting issues detected

═══════════════════════════════════════════════════════════
  OVERALL HEALTH: ✅ PASS
═══════════════════════════════════════════════════════════
```

---

## Notes

- Ensure all validations run independently and results aggregated
- Refer to `AGENTS.md` for specific command arguments (e.g., verbose flags, JSON output)
