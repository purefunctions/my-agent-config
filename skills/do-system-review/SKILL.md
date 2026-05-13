---
name: do-system-review
description: Analyze implementation against plan for process improvements
argument-hint: plan-file execution-report
---

# System Review

Perform a meta-level analysis of how well the implementation followed the plan and identify process improvements.

## Purpose

**System review is NOT code review.** You're not looking for bugs in the code - you're looking for bugs in the process.

**Your job:**

- Analyze plan adherence and divergence patterns
- Identify which divergences were justified vs problematic
- Surface process improvements that prevent future issues
- Suggest updates to Layer 1 assets (AGENTS.md, CLAUDE.md or other AI coding guidelines, plan templates, commands)

**Philosophy:**

- Good divergence reveals plan limitations → improve planning
- Bad divergence reveals unclear requirements → improve communication
- Repeated issues reveal missing automation → create commands

## Context & Inputs

You will analyze four key artifacts:

**Plan Command:**
Read this to understand the planning process and what instructions guide plan creation.
Load the do-feature-plan skill for reference

**Generated Plan:**
Read this to understand what the agent was SUPPOSED to do.
Plan file: $1

**Execute Command:**
Read this to understand the execution process and what instructions guide implementation.
Load the do-plan-execution skill for reference

**Execution Report:**
Read this to understand what the agent ACTUALLY did and why.
Execution report: $2

## Analysis Workflow

### Step 1: Understand the Planned Approach

Read the generated plan ($1) and extract:

- What features were planned?
- What architecture was specified?
- What validation steps were defined?
- What patterns were referenced?

### Step 2: Understand the Actual Implementation

Read the execution report ($2) and extract:

- What was implemented?
- What diverged from the plan?
- What challenges were encountered?
- What was skipped and why?

### Step 3: Classify Each Divergence

For each divergence identified in the execution report, classify as:

**Good Divergence ✅** (Justified):

- Plan assumed something that didn't exist in the codebase
- Better pattern discovered during implementation
- Performance optimization needed
- Security issue discovered that required different approach

**Bad Divergence ❌** (Problematic):

- Ignored explicit constraints in plan
- Created new architecture instead of following existing patterns
- Took shortcuts that introduce tech debt
- Misunderstood requirements

### Step 4: Trace Root Causes

For each problematic divergence, identify the root cause:

- Was the plan unclear, where, why?
- Was context missing, where, why?
- Was validation missing, where, why?
- Was manual step repeated, where, why?

### Step 5: Generate Process Improvements

Based on patterns across divergences, suggest:

- **AI guidelines updates (AGENTS.md, CLAUDE.md, etc):** Universal patterns or anti-patterns to document
- **Plan command updates:** Instructions that need clarification or missing steps
- **New commands:** Manual processes that should be automated
- **Validation additions:** Checks that would catch issues earlier

## Noise Filtering Criteria

**ONLY report improvements that meet ALL of these criteria:**

1. **Pattern-based (not one-off):** The issue appeared 2+ times OR would clearly prevent future similar issues
2. **High impact:** The divergence caused significant rework, bugs, or violated core architectural principles
3. **Actionable:** You can specify exactly which file and section needs updating, with specific text to add
4. **Prevention-focused:** The improvement prevents concrete future problems, not just "nice to have"

**SKIP reporting:**
- Style/formatting issues (covered by linters)
- Divergences where agent discovered and used existing better patterns
- One-off situational decisions that worked well
- Vague suggestions like "consider" or "maybe" without specific actions
- Minor optimizations that didn't cause problems

**Limit output:**
- Maximum 5 improvements per category (AI guidelines, plan command, new commands, validation)
- If more than 5, rank by impact and report only top 5

## Output Format

Save your analysis to: `.agent-config/user/artifacts/system-reviews/[feature-name]-review.md`

### Report Structure:

#### Meta Information

- Plan reviewed: [path to $1]
- Execution report: [path to $2]
- Date: [current date]

#### Overall Alignment Score: \_\_/10

Scoring guide:

- 10: Perfect adherence, all divergences justified
- 7-9: Minor justified divergences
- 4-6: Mix of justified and problematic divergences
- 1-3: Major problematic divergences

#### Divergence Analysis

For each divergence from the execution report:

```yaml
divergence: [what changed]
planned: [what plan specified]
actual: [what was implemented]
reason: [agent's stated reason from report]
classification: good ✅ | bad ❌
justified: yes/no
root_cause: [unclear plan | missing context | etc]
```

#### Pattern Compliance

Assess adherence to documented patterns (only report violations that caused problems):

- [ ] Followed codebase architecture
- [ ] Used documented patterns (from AGENTS.md or similar AI coding guidelines)
- [ ] Applied testing patterns correctly
- [ ] Met validation requirements

#### System Improvement Actions

**ONLY include improvements that passed noise filtering criteria above.**

Based on analysis, recommend specific actions (max 5 per category, ranked by impact):

**Update AI Coding Guidelines (AGENTS.md or similar):**

- [ ] Document [pattern X] at [specific section] - prevents [concrete problem Y]
- [ ] Add anti-pattern warning for [Y] in [section Z] - prevents [problem]
- [ ] Clarify [technology constraint Z] - prevented by [evidence]

**Update Plan Command (Load the do-feature-plan skill for reference):**

- [ ] Add instruction for [missing step] at line [X] - prevents [problem]
- [ ] Clarify [ambiguous instruction] at line [Y] - prevents [problem]
- [ ] Add validation requirement for [X] - prevents [problem]

**Create New Command:**

- [ ] `/[command-name]` for [manual process repeated 3+ times] - saves [time/prevents errors]

**Update Execute Command (Load the do-plan-execution skill for reference):**

- [ ] Add [validation step] to execution checklist - prevents [problem]

#### Key Learnings

**What worked well:**

- [specific things that went smoothly]

**What needs improvement:**

- [specific process gaps identified]

**For next implementation:**

- [concrete improvements to try]

## Important

- **Be specific:** Don't say "plan was unclear" - say "plan didn't specify which auth pattern to use at step 3"
- **Focus on patterns:** One-off issues aren't actionable. Look for repeated problems or clear preventable issues.
- **Action-oriented:** Every finding must have a concrete asset update suggestion and the contrete problem it prevents (with evidence from this execution), with specific text to add or change
- **High signal-to-noise:** Apply filtering criteria strictly. Better to have 3 high-impact improvements than 20 low-value suggestions.
- **Suggest improvements:** Don't just analyze - actually draft the text to add to AGENTS.md (CLAUDE.md or similar files) or commands