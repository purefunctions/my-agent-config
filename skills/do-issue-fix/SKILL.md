---
name: do-issue-fix
description: Fix a described bug or issue
argument-hint: description of the problem to fix
allowed-tools: Read, Write, Edit, Grep, Bash(uv run ruff:*), Bash(uv run pyright:*), Bash(uv run pytest:*), Bash(git:*)
---

# Fix Issue: Address a Described Problem

Fix a bug or issue based on a description provided by the user.

## Problem Description

**User's description**: $ARGUMENTS

## Phase 1: Understand the Problem

### 1.1 Analyze the Description

Parse the description to understand:
- **What's the problem**: What's broken or needs fixing?
- **Where it might be**: Any clues about location (file, function, module)?
- **Severity**: How critical is this issue?
  - **Critical**: "security", "vulnerability", "data corruption", "production down"
  - **High**: "bug", "error", "broken", "crash", "fails"
  - **Medium**: General issues, improvements
  - **Low**: "style", "formatting", "typo", "optimization"

### 1.2 Locate the Relevant Code

Search the codebase to find where the issue exists:

**Search strategy:**

**If LSP is available** (preferred for code navigation):
1. Extract key terms from description (function names, class names, symbols)
2. Use LSP "Go to Definition" or "Find References" to locate symbols directly
3. Use LSP "Find Symbol" to search across the workspace
4. Navigate to relevant code locations using LSP

**If LSP is not available** (fallback to text search):
1. Extract key terms from description (function names, module names, error messages)
2. Use Grep to find relevant files containing those terms
3. Read candidate files to understand context
4. Identify the exact location that needs fixing

**If you can't find the code:**
- Explain what you searched for (and which method you used)
- List what you found (or didn't find)
- Ask user for more specific location/context
- Don't guess or make random changes

### 1.3 Create Fix Plan

Once you've located the issue, create a plan:

**Confirm with user:**
- "I found the issue in `path/to/file.py:123`"
- "The problem is: [your understanding of the issue]"
- "I plan to fix it by: [your approach]"
- "Does this sound right?"

**Wait for confirmation** before proceeding (unless the issue is obvious and low-risk).

## Phase 2: Implement the Fix

### 2.1 Explain What You're Doing

Before making changes, clearly explain:
- **What was wrong**: Describe the bug/issue
- **Why it's a problem**: Explain the impact
- **What we'll do**: Describe the fix approach

### 2.2 Read the Current Code

Read the file(s) containing the issue to understand full context:
- Understand the function/module purpose
- Check for related code that might be affected
- Look for existing tests that cover this code

### 2.3 Apply the Fix

Make the necessary changes:
- Follow AGENTS.md standards
- Maintain existing code style and patterns
- Keep changes minimal and focused

**Show the fix:**
- Display the old code (what was wrong)
- Display the new code (what was fixed)
- Explain what changed and why

### 2.4 Add or Update Tests (if needed)

For bugs or logic changes:
- Add test case that would have caught the bug
- Or update existing tests if behavior changed
- Verify tests are in the right location (mirror source structure)

### 2.5 Verify the Fix

**For critical/high severity:**
- Run relevant tests immediately
- Verify the specific issue is resolved

**For medium/low severity:**
- Can defer to full validation in Phase 3

## Phase 3: Validate the Fix

### 3.1 Run Full Validation

Run the validate command to ensure nothing broke:

**See**: `Load the do-validation skill`

### 3.2 Fix Any Regressions

If validation fails:
- Identify what broke
- Fix the regression
- Re-run validation
- Continue until all validation passes

## Phase 4: Summary Report

After the fix is complete and validated, provide summary:

### Fix Applied

**Problem described**: 
- "[user's original description]"

**Issue found in:**
- `path/to/file.py:123`

**Severity**: [critical|high|medium|low]

**What was fixed:**
- Brief explanation of the change made

**Files modified:**
- `path/to/file1.py` (fix applied)
- `tests/path/to/test_file1.py` (test added/updated)

### Validation Results

Reference the validation report output.

### Ready for Commit

All fixes applied and validated. Use `/do-commit` to create a commit.

## Important Guidelines

**Be certain before making changes:**
- ✅ Locate the actual code causing the problem
- ✅ Understand the issue before fixing it
- ✅ Confirm your understanding with the user if unclear
- ❌ Don't guess at locations or make random changes

**Search systematically:**
- ✅ Prefer LSP for code navigation when available
- ✅ Use Grep as fallback for text-based search
- ❌ Don't assume where code lives without searching

**Maintain quality:**
- ✅ Follow existing code patterns in the file
- ✅ Respect AGENTS.md standards
- ✅ Keep fixes minimal and focused
- ✅ Add tests for bugs to prevent regression

**Communication:**
- 📢 Explain what you found and where
- 📢 Describe your fix plan before implementing
- 📢 Ask for clarification if description is vague
- 📢 Show the before/after of your changes

## Edge Cases

**Vague description:**
- Search for likely locations
- List what you found
- Ask user for clarification: "Did you mean this code in X, or that code in Y?"

**Multiple possible locations:**
- List all candidates
- Ask user which one they meant
- Or fix all if they're all clearly wrong

**Issue doesn't exist (anymore):**
- Explain what you searched for
- Note that the issue may already be fixed
- Ask user if they want you to verify it's working correctly

**Fix requires breaking changes:**
- Explain why breaking change is necessary
- Show impact (what code will need updating)
- Get user approval before proceeding

**Can't find the issue at all:**
- List everything you searched for
- Explain what you found (or didn't find)
- Ask for more specific details:
  - File name or path hints
  - Function or class names
  - Error messages or stack traces
  - Steps to reproduce

---

**Ready to fix? Let's find and resolve that issue!**
