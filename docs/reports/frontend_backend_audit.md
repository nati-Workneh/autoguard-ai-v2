# Frontend/Backend Integration Audit

## Scope

This audit checks the browser-to-API integration for the quick-predict flow
only. It does not touch the model, the predictor, or any frozen artifact.

## 1. Which endpoint does the UI call?

`frontend/static/app.js:715` — `fetchJson("/api/quick-predict", ...)`.

There is exactly one fetch call wired to the `quick-predict-form` submit
handler (`submitQuickPredict`, `app.js:691-735`). No other code path in
`app.js` calls `/api/predict`. The form element id (`app.js:3`,
`index.html:66`) is `quick-predict-form`, and the only submit listener bound
to it is `submitQuickPredict`.

**Answer: the browser hits the correct endpoint** (`/api/quick-predict`, not
`/api/predict`).

## 2. Request payload shape

`buildPayload()` (`app.js:295-305`) sends:

```json
{
  "license_plate": "<digits only>",
  "driver_age": <number>,
  "policy_tenure": <number>,
  "city": "<canonical Hebrew city name>"
}
```

This matches `QuickPredictRequest` (`backend/schemas/quick_predict.py:10-26`)
field-for-field, including types. `extra="forbid"` is set on the schema, and
`buildPayload()` only ever emits these four keys, so no extra-field rejection
is possible from this path.

## 3. Response parsing logic

`fetchJson()` (`app.js:196-210`) parses based on `content-type`. The backend
always returns `application/json` for both success (`QuickPredictResponse`)
and error responses (`JSONResponse` exception handlers in `backend/main.py`),
so this branch is consistent — no JSON/text parsing mismatch.

`renderDashboard(payload, body)` (`app.js:727`) is only called when
`response.ok` is true, and reads `body.vehicle`, `body.prediction`,
`body.top_risk_drivers`, `body.metadata` — all present in
`QuickPredictResponse` (`backend/schemas/quick_predict.py:68-76`).

## 4. Error handling logic

`submitQuickPredict` (`app.js:691-735`):

- `!response.ok` → `formatApiError(body)` → shown via `showFormError`.
- network/throw exceptions → `UI_TEXT.networkFailure` (same Hebrew string as
  the generic fallback).

This is a deliberate two-path design (HTTP error vs. network/JS exception),
not a bug — both surface a Hebrew message, by design from Sprint 8.9.1.

## 5. Are success responses ever routed into the error path?

No. The branch is a plain `if (!response.ok) { ...; return; }` followed by
`renderDashboard(...)` on the line below. There is no code between the fetch
and this check that could throw on a 200 response and get caught by the
`catch` block — `fetchJson` only awaits `response.json()`/`response.text()`,
both of which succeed for the actual response shape returned by
`/api/quick-predict`.

## 6/7/8. Live capture — direct API call vs. browser call

Reproduced with the exact values from the bug report
(`license_plate=9691464, driver_age=34, policy_tenure=1, city=ירושלים`):

**Direct API call (curl):**

```
POST /api/quick-predict
{"license_plate":"9691464","driver_age":34,"policy_tenure":1,"city":"ירושלים"}

200 OK
{"vehicle":{"manufacturer":"סוזוקי-יפן","commercial_model":"SWIFT","production_year":2008}, ...
 "prediction":{"claim_probability":0.297744,"risk_level":"Low","recommendation":"Standard approval"}, ...}
```

**Browser call (Playwright, driving the real form — fill fields, select
city from the autocomplete list returned by `/api/city-options`, click
"נתח סיכון"):**

```
>> REQUEST POST http://127.0.0.1:8000/api/quick-predict
>> BODY {"license_plate":"9691464","driver_age":34,"policy_tenure":1,"city":"ירושלים"}
<< RESPONSE 200 http://127.0.0.1:8000/api/quick-predict
<< BODY {"vehicle":{"manufacturer":"סוזוקי-יפן",...},"prediction":{"claim_probability":0.297744,"risk_level":"Low",...}, ...}
FORM ERROR TEXT: (empty — no error banner shown, dashboard rendered)
```

The request payload, response payload, and response status are **identical**
between the direct call and the browser call.

## Answers

- **Does the browser hit the correct endpoint?** Yes — `/api/quick-predict`.
- **Does the browser receive a successful response?** Yes — `200 OK` with a
  fully populated `QuickPredictResponse`, captured live above.
- **If yes, why is the UI still showing an error?** In this environment, it
  isn't. The premise of "browser UI still reports a failure" did not
  reproduce against the current `frontend/static/app.js` +
  `backend/main.py` integration, with a fresh server process and a fresh
  browser session, network-traced end to end.
- **Exact file and line responsible:** None found — no defect exists in the
  traced integration path for the given inputs.

## Conclusion

No frontend/backend integration bug was found for the reported
license_plate/driver_age/policy_tenure/city combination. The endpoint,
payload shape, response parsing, and error-routing logic are all correct and
consistent with the frozen contract. If the failure is still visible to a
user, the most likely explanations are environmental, not code-level:

- a stale cached copy of `app.js` in the browser (hard refresh required),
- a different/older server process still bound to the port being used,
- an intermittent failure further upstream (the live `data.gov.il` vehicle
  registry call), unrelated to this integration layer.

No code was changed as part of this audit.
