# Frontend - Domain Rules

> Domain rules for the future underwriting assistant interface.

---

## Scope

Everything under `frontend/static/`:

- input form
- styling
- client-side submission logic
- result rendering

Current constraint: frontend implementation is frozen in the current phase.

---

## Owner Tag

`[DEV:frontend]`

---

## Planned Responsibilities

1. build an underwriting form from the finalized raw input contract
2. collect only approved business inputs; never expose `policy_id` as a manual
   field
3. submit requests asynchronously to `POST /api/predict`
4. render:
   - claim probability
   - review recommendation
   - model or response metadata if exposed
5. stay accessible, responsive, and form-heavy rather than marketing-heavy

---

## Rules

- Do not reuse the legacy six-dropdown car form.
- Wait for the finalized preprocessing manifest before locking field options or
  validation rules.
- The frontend never performs encoding, scaling, or model logic.
- Any categorical choices shown in the UI must come from the approved artifact
  contract, not memory or copy-paste from old docs.
- Show validation and request errors inline.
- Use semantic labels and grouped sections because the future form will contain
  many more fields than the legacy project.

---

## Testing Expectations

- End-to-end tests for the form submission flow
- Error-state rendering tests
- Responsive layout checks
