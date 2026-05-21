# Design Smells

A design smell matters only when it predicts future human maintenance pain. Do not report smells as style preferences.

## 1. Speculative abstraction

Symptom:

- Architecture, layers, factories, registries, strategies, or interfaces are added for hypothetical scale.

Maintenance risk:

- More files, indirection, and concepts without current payoff.

Preferred response:

- Replace with direct code or a small seam.

## 2. Shallow module

Symptom:

- A wrapper mostly forwards calls or renames things without hiding meaningful complexity.

Maintenance risk:

- Adds navigation cost without reducing caller burden.

Preferred response:

- Remove it, deepen it, or move real complexity behind it.

## 3. Under-designed patch

Symptom:

- A local fix adds conditionals, duplication, special cases, or scattered knowledge.

Maintenance risk:

- The next related change becomes harder and more error-prone.

Preferred response:

- Use the smallest strategic fix.

## 4. Information leakage

Symptom:

- Callers must know storage details, lifecycle rules, validation rules, ordering constraints, cache/retry behavior, or internal states.

Maintenance risk:

- Internal changes require caller changes.

Preferred response:

- Move the knowledge into the owning module.

## 5. Shared meaning duplicated

Symptom:

- The same domain rule, invariant, policy, or likely future change appears in multiple places.

Maintenance risk:

- Future edits must be coordinated manually.

Preferred response:

- Extract a modest named abstraction.

## 6. Shape-only abstraction

Symptom:

- Code is abstracted because it looks similar, not because it represents the same concept.

Maintenance risk:

- Different concepts become coupled and harder to evolve independently.

Preferred response:

- Inline it or split by concept.

## 7. Flag/mode explosion

Symptom:

- Behavior is controlled by flags, modes, options, or subtle combinations.

Maintenance risk:

- Callers must understand too many execution paths.

Preferred response:

- Define away the special case, move the decision inward, or split APIs.

## 8. Leaky interface

Symptom:

- The API exposes implementation details or forces fragile call sequences.

Maintenance risk:

- The interface is harder to use correctly than it should be.

Preferred response:

- Make the caller express intent and hide mechanics inside the module.

## 9. Comment noise

Symptom:

- Comments restate code, explain obvious behavior, or use verbose filler.

Maintenance risk:

- Readers spend attention without learning intent.

Preferred response:

- Keep comments only for intent, invariants, constraints, surprising choices, and trade-offs.

## 10. Verbose ceremony

Symptom:

- Too many files, classes, helpers, or layers for the problem size.

Maintenance risk:

- Human readers must navigate structure that does not pay for itself.

Preferred response:

- Collapse structure until every layer pays rent.
