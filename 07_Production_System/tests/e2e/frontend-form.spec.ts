import { test, expect } from "@playwright/test";

/**
 * Sprint 9B rewrite. The previous version of this spec targeted a frontend
 * that no longer exists: #driver_age/#policy_tenure/#city fields and the
 * deprecated V1 /api/quick-predict + /api/city-options endpoints. The
 * current V2 frontend uses a license-plate lookup (no city field, no
 * policy_tenure), real-years driver inputs, and /api/v2/quick-predict.
 * There is also a gated landing screen (#enter-app-button) that must be
 * dismissed before the form is interactive -- the old spec didn't account
 * for this either.
 */

const VALID_PAYLOAD = {
  license_plate: "1234567",
  age: "34",
  driving_experience_years: "10",
  past_accidents: "0",
  speeding_violations: "0",
  duis: "0",
  annual_mileage: "15000",
};

async function enterApp(page: import("@playwright/test").Page) {
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  const enterButton = page.locator("#enter-app-button");
  if (await enterButton.isVisible().catch(() => false)) {
    await enterButton.click();
  }
  await expect(page.locator("#license_plate")).toBeVisible();
}

async function fillValidForm(page: import("@playwright/test").Page, overrides: Partial<typeof VALID_PAYLOAD> = {}) {
  const values = { ...VALID_PAYLOAD, ...overrides };
  await page.locator("#license_plate").fill(values.license_plate);
  await page.locator("#age").fill(values.age);
  await page.locator("#driving_experience_years").fill(values.driving_experience_years);
  await page.locator("#past_accidents").fill(values.past_accidents);
  await page.locator("#speeding_violations").fill(values.speeding_violations);
  await page.locator("#duis").fill(values.duis);
  await page.locator("#annual_mileage").fill(values.annual_mileage);
  await page.locator('input[name="vehicle_ownership"][value="private"]').check();
}

function mockQuickPredictSuccess(page: import("@playwright/test").Page, overrides: Record<string, unknown> = {}) {
  return page.route("**/api/v2/quick-predict", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        vehicle: { manufacturer: "Toyota", commercial_model: "Corolla", production_year: 2021, vehicle_year_category: "after 2015" },
        prediction: { claim_probability: 0.612, risk_level: "High", recommendation: "Manual underwriting review" },
        premium_impact: { direction: "surcharge", min_percent: 10, max_percent: 25, estimated_percent: 18.4, summary: "Estimated surcharge of 18.4% (range 10%-25%)" },
        top_risk_drivers: [
          { title: "Driving experience", direction: "increase", detail: "Limited driving experience is the strongest contributor to higher predicted risk." },
        ],
        metadata: { model_version: "v3.0.0-50k", model_name: "AutoGuard AI V2 Production Model", prediction_timestamp: "2026-08-04T12:00:00Z" },
        ...overrides,
      }),
    });
  });
}

test.describe("AutoGuard AI V2 production dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/v2/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "ok", model_loaded: true, model_name: "AutoGuard AI V2 Production Model", model_version: "v3.0.0-50k" }),
      });
    });
  });

  test("loads the V2 dashboard shell behind the landing gate", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await expect(page).toHaveTitle(/AutoGuard AI/i);
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");

    // Landing screen gates the app until #enter-app-button is clicked.
    await expect(page.locator("#enter-app-button")).toBeVisible();
    await page.locator("#enter-app-button").click();

    await expect(page.locator("#license_plate")).toBeVisible();
    await expect(page.locator("#age")).toBeVisible();
    await expect(page.locator("#driving_experience_years")).toBeVisible();
    await expect(page.locator("#past_accidents")).toBeVisible();
    await expect(page.locator("#speeding_violations")).toBeVisible();
    await expect(page.locator("#duis")).toBeVisible();
    await expect(page.locator("#annual_mileage")).toBeVisible();
    await expect(page.locator('input[name="vehicle_ownership"]')).toHaveCount(3);
    await expect(page.locator("#health-label")).toHaveText("המערכת פעילה");
  });

  test("empty submission shows license-plate validation guidance", async ({ page }) => {
    await enterApp(page);
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("יש להזין מספר רכב.");
    await expect(page.locator("#result-dashboard")).toBeHidden();
  });

  test("out-of-range driver age is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await fillValidForm(page, { age: "15" });
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("גיל הנהג חייב להיות בין 18 ל-100");
  });

  test("driving experience exceeding age-16 is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await fillValidForm(page, { age: "20", driving_experience_years: "10" }); // max plausible is age-16=4
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toContainText("שנות הנהיגה");
  });

  test("negative past accidents is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await fillValidForm(page, { past_accidents: "-1" });
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("מספר התאונות בעבר חייב להיות 0 ומעלה");
  });

  test("negative speeding violations is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await fillValidForm(page, { speeding_violations: "-1" });
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("מספר דוחות המהירות חייב להיות 0 ומעלה");
  });

  test("negative DUIs is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await fillValidForm(page, { duis: "-1" });
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("מספר עבירות הנהיגה בשכרות חייב להיות 0 ומעלה");
  });

  test("non-positive annual mileage is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await fillValidForm(page, { annual_mileage: "0" });
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("יש להזין קילומטראז' שנתי חיובי");
  });

  test("missing ownership selection is rejected client-side", async ({ page }) => {
    await enterApp(page);
    await page.locator("#license_plate").fill(VALID_PAYLOAD.license_plate);
    await page.locator("#age").fill(VALID_PAYLOAD.age);
    await page.locator("#driving_experience_years").fill(VALID_PAYLOAD.driving_experience_years);
    await page.locator("#past_accidents").fill(VALID_PAYLOAD.past_accidents);
    await page.locator("#speeding_violations").fill(VALID_PAYLOAD.speeding_violations);
    await page.locator("#duis").fill(VALID_PAYLOAD.duis);
    await page.locator("#annual_mileage").fill(VALID_PAYLOAD.annual_mileage);
    // deliberately do not select an ownership radio
    await page.locator("#analyze-button").click();
    await expect(page.locator("#form-error")).toHaveText("יש לבחור סוג בעלות על הרכב");
  });

  test("submits a valid V2 quick-predict request and renders the result dashboard", async ({ page }) => {
    await mockQuickPredictSuccess(page);
    await enterApp(page);
    await fillValidForm(page);

    await page.locator("#analyze-button").click();
    await expect(page.locator("#analyze-button")).toHaveText("מבצע הערכת סיכון...");
    await expect(page.locator("#result-dashboard")).toBeVisible();
    await expect(page.locator("#vehicle-manufacturer")).toHaveText("Toyota");
    await expect(page.locator("#vehicle-commercial-model")).toHaveText("Corolla");
    await expect(page.locator("#claim-probability")).toHaveText("61.2%");
    await expect(page.locator("#risk-level")).toHaveText("סיכון גבוה");
    await expect(page.locator("#recommendation")).toHaveText("נדרשת בדיקה מעמיקה");
    await expect(page.locator("#top-risk-drivers .driver-item")).toHaveCount(1);
    await expect(page.locator("#premium-impact-summary")).toContainText("18.4%");
    await expect(page.locator("#model-version")).toHaveText("v3.0.0-50k");
    await expect(page.locator("#technical-details")).not.toHaveAttribute("open", "");
  });

  test("clear/reset returns the form and dashboard to their initial empty state", async ({ page }) => {
    await mockQuickPredictSuccess(page);
    await enterApp(page);
    await fillValidForm(page);
    await page.locator("#analyze-button").click();
    await expect(page.locator("#result-dashboard")).toBeVisible();

    await page.locator("#clear-button").click();

    await expect(page.locator("#license_plate")).toHaveValue("");
    await expect(page.locator("#result-dashboard")).toBeHidden();
    await expect(page.locator("#result-empty")).toBeVisible();
    await expect(page.locator(".empty-title")).toHaveText("המערכת מוכנה לביצוע הערכת סיכון");
  });

  test("vehicle-not-found API response shows a business-friendly message", async ({ page }) => {
    await page.route("**/api/v2/quick-predict", async (route) => {
      await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "vehicle not found for the provided license plate" }) });
    });
    await enterApp(page);
    await fillValidForm(page);
    await page.locator("#analyze-button").click();

    await expect(page.locator("#form-error")).toHaveText("לא נמצא רכב התואם למספר שהוזן.");
    await expect(page.locator("#result-dashboard")).toBeHidden();
  });

  test("upstream registry failure (504) shows a delayed-lookup message, not a raw error", async ({ page }) => {
    await page.route("**/api/v2/quick-predict", async (route) => {
      await route.fulfill({ status: 502, contentType: "application/json", body: JSON.stringify({ detail: "vehicle registry request timed out" }) });
    });
    await enterApp(page);
    await fillValidForm(page);
    await page.locator("#analyze-button").click();

    await expect(page.locator("#form-error")).toHaveText("איתור פרטי הרכב מתעכב, נסו שוב בעוד רגע");
    await expect(page.locator("#form-error")).not.toContainText("Traceback");
    await expect(page.locator("#result-dashboard")).toBeHidden();
  });

  test("network failure (fetch rejects) shows a generic unavailable message, not a crash", async ({ page }) => {
    await page.route("**/api/v2/quick-predict", async (route) => {
      await route.abort("failed");
    });
    await enterApp(page);
    await fillValidForm(page);
    await page.locator("#analyze-button").click();

    await expect(page.locator("#form-error")).toHaveText("לא ניתן להשלים את הערכת הסיכון כעת.");
  });
});
