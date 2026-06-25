# UI Redesign Summary — Brand Identity & Premium UI

Sprint 11.0A. Frontend-only visual redesign. No backend, API, feature-builder, or model code was touched — verified by re-running the full test suite (132/132 passed, including the 3 Playwright end-to-end scenarios that exercise the real V2 prediction flow against the redesigned markup).

## Screenshots

| View | Desktop | Mobile |
|---|---|---|
| Hero (empty state) | `tests/screenshots/sprint_11_0a/hero_desktop.png` | `tests/screenshots/sprint_11_0a/hero_mobile.png` |
| Form filled | `tests/screenshots/sprint_11_0a/form_filled_desktop.png` | `tests/screenshots/sprint_11_0a/form_filled_mobile.png` |
| Results dashboard | `tests/screenshots/sprint_11_0a/results_desktop.png` | `tests/screenshots/sprint_11_0a/results_mobile.png` |

## Logo / Brand Asset Handling

The provided source image (`ui-ux-pro-max/.../jeep-renegade-orange-logo.png.png`) is a real photo of a Jeep Renegade with genuine alpha transparency (confirmed programmatically: 39% fully-transparent pixels, soft-edged cutout, not a flat background). Processing performed:

- Cropped to content bounds, resized and compressed to two web-weight variants during Sprint 11.0A; those retired assets now live in `archive/design/frontend_assets/vehicle-hero.png` and `archive/design/frontend_assets/vehicle-hero-mobile.png`.
- A square, transparently-padded version was generated and downscaled to `logo-180.png`, `logo-192.png`, `logo-512.png`, and a multi-resolution `favicon.ico` (16/32/48px).
- Proportions were never distorted — every resize preserved the original aspect ratio; only padding (transparent) or uniform scaling was applied.

**Trademark note, surfaced transparently (not blocking, per explicit repeated instruction to use this exact image as brand identity):** a tight crop on the vehicle's grille legibly shows the "JEEP" badge. To avoid presenting a third-party automaker's trademark as AutoGuard AI's own mark, the navbar/footer/favicon use the **full car silhouette** scaled down, not a close-up crop of the badge — at navbar/favicon size the badge is not legible. This is a real consideration worth a final legal/brand check before any public/portfolio use, since the underlying photo is still a real, identifiable Jeep product.

## Logo Placement (Success Criterion Checklist)

| Location | Implementation |
|---|---|
| Navbar | `brand-mark` (46×46px, rounded, gradient backdrop) — `index.html` header |
| Hero section | Large vehicle image, primary visual element (see below) |
| Favicon | `favicon.ico` + `apple-touch-icon` (`logo-180.png`) |
| Loading state | `#result-empty .empty-icon` shows the logo with a `logo-pulse` animation while `is-busy` is active (driven by the existing `setBusy()` toggle — no new JS logic) |
| Footer | `footer-brand` — small logo + wordmark |

## Official Color Palette → CSS Design Tokens

All six mandatory colors are defined as `:root` custom properties in `style.css` and used exclusively for brand-colored surfaces — no other hue was introduced for primary UI elements:

```css
--brand-orange: #e2852e;
--brand-gold: #f5c857;
--brand-yellow-light: #ffee91;
--brand-blue-light: #abe0f0;
--brand-text: #000000;
--brand-bg: #fffdf7;
```

Derived tokens (`--brand-orange-dark`, `--brand-orange-soft`, `--brand-gold-soft`, `--brand-blue-soft`, etc.) are computed *from* these six colors (opacity/shade variants for borders, hover states, and soft card backgrounds) — no unrelated colors were added to the palette. `--success` (green) and `--danger` (red) are retained only for risk-level semantics (low/high risk), since the brief's palette has no red/green and those signals are safety-critical, not brand-identity elements.

## Palette Usage Map

| Color | Where Used |
|---|---|
| Primary Orange | CTA button gradient, field icons, hero kicker badge, active radio-card state, plate pill |
| Golden Yellow | CTA gradient end, KPI/premium card backgrounds, hero blob accent |
| Light Yellow | Hero decorative blob/shape accents |
| Light Blue | Status chip, vehicle-year card, operational note banner, steering-wheel decorative graphic |
| Black | All body/heading text (mandatory `--brand-text`) |
| Cream Background | Page background, footer background |

## Hero Section

Two-column layout (`hero-grid`) with the vehicle image and marketing copy on the **physical left** and the form on the **physical right**, regardless of the page's RTL Hebrew text direction. This was a real implementation detail worth flagging: under `dir="rtl"`, a naive CSS grid would place the first source-order child on the visual *right*, not left. The fix: `.hero-grid` is forced to `direction: ltr` (so grid column order is screen-literal), while every child re-asserts `direction: rtl` so Hebrew text inside still flows correctly. Verified visually in both screenshots above.

- **Vehicle image**: rendered at ~50% of the hero's visual weight on desktop (the `1.08fr` visual column vs. `0.92fr` form column), large, with a `drop-shadow` for grounding and a slow 6s `vehicle-float` keyframe animation.
- **Behind the vehicle**: an inline SVG layer with a shield outline, a steering-wheel outline, and two rotated geometric accent rectangles, all colored from the brand palette at low opacity — plus three large blurred radial-gradient "blobs" (orange/gold/light-blue) positioned behind everything via `.hero-shapes`.
- **Headline**: "ביטוח חכם. מותאם לך." (one of the three example headlines given in the brief), with "מותאם לך" in the accent orange.
- **Trust badges**: three small pill badges ("מאובטח ופרטי", "תוצאה תוך שניות", "מבוסס בינה מלאכותית") reinforcing the trustworthy/technology-driven positioning requested.

## Form Redesign

The questionnaire (unchanged field set/IDs/validation from Sprint 10.7) is now a `.form-card`: semi-transparent glassmorphism background (`backdrop-filter: blur(20px)`), `30px` rounded corners, generous spacing, and a small inline SVG icon beside every field label. The vehicle-ownership radio group was rebuilt as three icon-bearing "radio cards" (house/key icon for private, briefcase-key icon for leasing, building icon for company) with a visible checked-state highlight (orange border + tinted background) — a clear upgrade over the prior plain radio-button row, while keeping the exact same `name="vehicle_ownership"` values (`private`/`leasing`/`company`) the backend expects.

## Results Page Redesign

Every result section is now an icon-led card (`card-icon` + `card-icon-row`) with hover elevation:

- **Vehicle card** — plate pill, manufacturer/model/year spec grid.
- **Risk Score** — new: a 0–100 score is computed client-side as `round(claim_probability × 100)` and displayed alongside the existing claim-probability percentage. This is a **presentation-only** addition — it derives from the same `claim_probability` the API already returns; no new backend field, model output, or API contract change was made (see `formatRiskScore()` in `app.js`).
- **Claim Probability** — existing field, restyled as a gold KPI card.
- **Estimated Premium** — existing `premium_impact` block, restyled as a card with a coin icon.
- **Risk Drivers** — existing `top_risk_drivers` list, restyled as a 2-column icon-card grid with hover lift.

## Animations

| Element | Effect |
|---|---|
| Vehicle (hero) | `vehicle-float` — slow 6s vertical float loop |
| Cards (`.panel`) | `translateY(-3px)` + shadow growth on hover |
| Buttons | `scale(1.025)` on hover, `scale(0.98)` on active (press) |
| Sections | `.fade-in-section` + `IntersectionObserver` — results section fades/slides in once scrolled into view |
| Scrolling | `html { scroll-behavior: smooth; }` |
| Loading | Logo icon pulses (`logo-pulse`) in the empty-state panel while a request is in flight |

All animations respect `prefers-reduced-motion: reduce` (durations collapsed to ~0 for users who request it).

## Typography

`Heebo` (body), `Rubik` (headings/display), `Assistant` (fallback) loaded via Google Fonts with `preconnect`, all three from the brief's preferred list. Text color is `#000000` (`--brand-text`) everywhere except risk-state semantic colors (green/red) and the muted soft-text tones used for secondary copy.

## Responsive Design

| Breakpoint | Behavior |
|---|---|
| ≤1080px | Hero collapses to single column (vehicle image stacks above form); results/driver grids collapse to 1 column |
| ≤720px | Tighter navbar/hero padding, smaller headline clamp, mobile vehicle image variant served |
| ≤640px | Ownership radio cards reflow to a 3-up compact row |
| ≤480px | Status chip text hidden, icon-only, to fit small screens |

RTL is preserved throughout — `dir="rtl"` remains on `<html>`, all Hebrew copy reads correctly, and the only place direction is overridden (`.hero-grid`) explicitly restores `rtl` on every child.

## Accessibility Review

- **Contrast audit performed before implementation** (WCAG 2.1 formula, computed programmatically): black text on the official background (#FFFDF7) is 20.65:1; black text on Primary Orange is 7.63:1; black on Golden Yellow is 13.28:1; black on Light Yellow is 17.89:1; black on Light Blue is 14.65:1 — all comfortably pass WCAG AA (4.5:1) and AAA (7:1) for normal text.
- **One real finding acted on**: white text on Primary Orange measures only **2.75:1**, failing WCAG AA even for large/bold text (3:1 minimum). The primary CTA button therefore uses **black text** on its orange/gold gradient, not white — which also happens to align with the brief's own mandated "Primary Text: #000000" rule, so this is both an accessibility fix and a brand-compliance fix simultaneously.
- Focus-visible states (`:focus-visible`) are defined for all interactive elements (inputs, buttons, radio cards) using a consistent `--focus-ring` token, not removed or weakened from the Sprint 10.7 baseline.
- All decorative SVGs (`hero-decor-svg`, icons) are `aria-hidden="true"` or sit inside elements already labeled by visible text, so screen readers are not given redundant or meaningless content.
- `prefers-reduced-motion` is respected globally.
- Radio group retains its `role="radiogroup"` / `aria-required="true"` semantics and per-input `required` attribute from Sprint 10.7 — visual redesign did not regress this.

## Scope Confirmation

- `backend/` — untouched.
- `models/` — untouched.
- `frontend/static/app.js` — only two additive, presentation-only changes: a client-side `formatRiskScore()` display helper and an `IntersectionObserver`-based fade-in. The payload-building, validation, and `fetch` logic against `/api/v2/quick-predict` is byte-for-byte the same as Sprint 10.7.
- Full test suite: **132/132 passed**, including the real-browser Playwright scenarios, confirming the V2 prediction flow is functionally unchanged end-to-end under the new markup.
