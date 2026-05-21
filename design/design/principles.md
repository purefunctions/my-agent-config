# Software Design Principles for Agents

## Goal

Produce code that humans can maintain without regret.

## Core design rule

Choose the smallest design that survives the next plausible change.

Design beyond the current feature only when there is concrete evidence: known follow-up work, an existing second use case, repeated logic that represents the same domain idea, a stable concept worth naming, an invariant that must remain consistent, or a clear product/architecture direction.

When future need is plausible but unproven, preserve optionality with a seam, not an architecture.

## Design calibration

Good design is calibrated: not clever, not careless.

- Do not over-engineer for hypothetical scale.
- Do not under-design when a small abstraction would reduce repeated meaning.
- Avoid code that feels verbose, ceremonial, or harder for humans to own.
- Avoid code that is locally quick but globally weakening.

## Abstractions

Abstractions must pay rent. A new abstraction is justified only when it does at least one of these:

1. Hides real complexity from callers.
2. Gives a stable domain concept a clear name.
3. Centralizes an invariant or policy that must stay consistent.
4. Reduces future coordinated edits across multiple places.
5. Makes the caller-facing interface simpler than the implementation behind it.

Avoid abstractions that mainly:

- Add a layer because it looks professional.
- Wrap one call without hiding meaningful complexity.
- Exist for hypothetical scale.
- Require readers to jump across more files without reducing cognitive load.

## Module depth and interfaces

Prefer deep modules: simple interface, useful hidden complexity.

A good interface lets callers express intent. It should not force callers to know storage details, lifecycle rules, ordering constraints, retry/cache mechanics, validation internals, or subtle domain exceptions unless those are truly caller responsibilities.

## Complexity ownership

Push complexity into the module that can hide it best.

Keep policies, invariants, lifecycle rules, and implementation details owned in one place. When the same assumption appears across call sites, move that knowledge into the module that owns it.

## Duplication

Abstract shared meaning, not shared shape.

Similar code is not always duplication. Duplication should be removed when it represents the same domain rule, invariant, policy, or likely future change. The deciding question is: would a future human need to update both places for the same reason?

## Options and special cases

Options, modes, and flags are complexity. Add them only when they reduce more complexity than they create.

Preferred order:

1. Define the special case out of existence if possible.
2. Move the decision inside the owning module.
3. Use separate clearly named methods or types if behaviors are meaningfully different.
4. Use a flag only when it is truly the simplest caller-facing expression.

## Tactical vs strategic

Prefer the smallest change that improves the design direction, not merely the smallest code diff.

When a local fix works but adds conditionals, duplication, flags, hidden coupling, or scattered knowledge, compare it against a small strategic fix. If the larger redesign is clearly better but too broad, say so instead of sneaking it into the current task.

## Comments

Comments should explain intent, invariants, constraints, surprising choices, and trade-offs. Do not comment what the code already says.

Compact, not cryptic.

## Evidence requirement

No design vocabulary without code evidence and human-maintenance impact.

Weak:

```text
This improves information hiding.
```

Better:

```text
Callers no longer need to know retry/cache behavior; that logic now lives inside FooClient.
```
