# Design Calibration Examples

These examples teach the middle path: not clever, not careless.

Each example shows:

1. Under-designed version.
2. Over-engineered version.
3. Preferred maintainable version.
4. Rule taught.

## 1. Duplication vs shared meaning

Situation:

- Several callers validate that a workspace name is non-empty, lowercase, and does not contain `/`.

Under-designed:

```python
# caller_a.py
if not name or "/" in name or name != name.lower():
    raise ValueError("invalid workspace name")

# caller_b.py
if not name or "/" in name or name != name.lower():
    raise ValueError("invalid workspace name")
```

Why it hurts:

- The same domain invariant is duplicated. Future changes need coordinated edits.

Over-engineered:

```python
class ValidationRule: ...
class RuleRegistry: ...
class WorkspaceNameRule(ValidationRule): ...
```

Why it hurts:

- A framework appears before there is evidence that validation needs runtime registration or composition.

Preferred:

```python
def validate_workspace_name(name: str) -> None:
    if not name or "/" in name or name != name.lower():
        raise ValueError("invalid workspace name")
```

Why it is better:

- One small named abstraction centralizes a real invariant without adding ceremony.

Rule taught:

- Abstract shared meaning, not shared shape.

## 2. Plausible future change

Situation:

- Current export supports CSV. Product direction suggests JSON may be added soon, but no second format exists yet.

Under-designed:

```python
def export_report(report):
    return ",".join(report.rows)
```

Why it hurts:

- CSV formatting is hardcoded into the public function and will likely spread.

Over-engineered:

```python
class ExportStrategy: ...
class ExportStrategyFactory: ...
class ExportPluginRegistry: ...
```

Why it hurts:

- A plugin architecture assumes scale that does not exist.

Preferred:

```python
def export_report(report):
    return _render_csv(report)

def _render_csv(report):
    return ",".join(report.rows)
```

Why it is better:

- The public behavior stays simple. A small seam exists where the next format could fit.

Rule taught:

- Plausible future need creates a seam, not an architecture.

## 3. Flag vs clearer API

Situation:

- Callers can either create a draft invoice or finalize an invoice.

Under-designed:

```python
def create_invoice(data, finalize=False):
    ...
```

Why it hurts:

- Callers must understand a mode flag and its consequences.

Over-engineered:

```python
class InvoiceCreationMode: ...
class DraftInvoiceCreator: ...
class FinalInvoiceCreator: ...
```

Why it hurts:

- Separate class hierarchy is too much for two intent-level operations.

Preferred:

```python
def create_draft_invoice(data):
    ...

def finalize_invoice(data):
    ...
```

Why it is better:

- The caller expresses intent. No ambiguous flag combinations.

Rule taught:

- Options are complexity. Add them only when they reduce more complexity than they create.

## 4. Shallow wrapper

Situation:

- A wrapper exists around an HTTP client.

Under-designed:

```python
response = http.post(url, json=payload, timeout=10)
if response.status_code == 409:
    ...
```

Why it hurts:

- Callers own retry, timeout, and status-code policy.

Over-engineered:

```python
class ApiClient:
    def post(self, url, payload):
        return http.post(url, json=payload)
```

Why it hurts:

- The wrapper mostly forwards calls and adds navigation cost.

Preferred:

```python
class WorkspaceClient:
    def create_workspace(self, request):
        response = self._post_with_retry("/workspaces", request)
        return self._parse_workspace_response(response)
```

Why it is better:

- The caller gets a domain operation. Retry and parsing policy are hidden.

Rule taught:

- Make the interface simpler than the implementation it hides.

## 5. Comment style

Situation:

- A commit marker must be written before marking an operation complete.

Under-designed:

```python
write_marker(path)
mark_complete(intent)
```

Why it hurts:

- The invariant is not visible where ordering matters.

Over-engineered:

```python
# This function writes the marker to the path and then marks the intent complete.
# It is important because the marker should be written first. The complete call
# then updates the intent to completed. This avoids problems.
write_marker(path)
mark_complete(intent)
```

Why it hurts:

- The comment is verbose and mostly restates the code.

Preferred:

```python
# Preserve facts-before-visibility: clients may observe completion immediately.
write_marker(path)
mark_complete(intent)
```

Why it is better:

- The comment names the invariant and why the order matters.

Rule taught:

- Comment intent and invariants, not obvious mechanics.

## 6. Tactical patch

Situation:

- A new import path needs special handling.

Under-designed:

```python
if source == "legacy":
    path = legacy_path(id)
elif source == "new":
    path = new_path(id)
# repeated in several callers
```

Why it hurts:

- The special case spreads across callers.

Over-engineered:

```python
class SourcePathResolverFactory:
    ...
```

Why it hurts:

- Broad factory structure is not justified by two paths.

Preferred:

```python
def resolve_source_path(source, id):
    if source == "legacy":
        return legacy_path(id)
    return new_path(id)
```

Why it is better:

- The policy is localized without creating a framework.

Rule taught:

- Prefer the smallest change that improves design direction.
