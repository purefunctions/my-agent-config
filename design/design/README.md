# Design reference docs

These files are canonical reference and calibration docs. They are not required runtime dependencies for the skills. The skills are intentionally self-contained so they work across tools that may only load `SKILL.md`.

Use these docs when:

- Editing or reviewing the design-related skills.
- Creating repo-specific `AGENTS.md` guidance.
- Adding calibration examples after correcting agent output.
- Running a system review and deciding whether a failure needs a rule, smell, example, or project-guidance update.
- Manually asking an agent for deeper design calibration.

Files:

- `principles.md`: canonical design doctrine.
- `design-risk-tiers.md`: canonical workflow tiers and required behavior.
- `design-smells.md`: detection-and-response catalog for maintainability risks.
- `examples.md`: three-way calibration examples: under-designed, over-engineered, preferred.

Rule: skills should embed the minimum needed instructions locally; these docs keep the shared doctrine coherent and help future edits avoid drift.
