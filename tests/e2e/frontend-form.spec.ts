import { test, expect } from "@playwright/test";

test.describe("AutoGuard AI production dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await page.route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          status: "ok",
          model_loaded: true,
          preprocessing_loaded: true,
          model_name: "Random Forest",
          model_version: "sprint_06_final_freeze_v1",
        }),
      });
    });

    await page.route("**/api/city-options", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          "תל אביב-יפו",
          "ירושלים",
          "חיפה",
          "באר שבע",
          "ראשון לציון",
        ]),
      });
    });
  });

  test("loads the Hebrew underwriting dashboard shell", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await expect(page).toHaveTitle(/AutoGuard AI/i);
    await expect(page.getByRole("heading", { name: "AutoGuard AI" })).toBeVisible();
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
    await expect(page.locator("#health-label")).toContainText("המערכת פעילה");
    await expect(page.getByRole("heading", { name: "בדיקת סיכון מהירה" })).toBeVisible();
    await expect(page.locator("#quick-predict-form input")).toHaveCount(4);
    await expect(page.locator("#quick-predict-form select")).toHaveCount(0);
  });

  test("submits quick predict with raw-year inputs and renders the dashboard", async ({ page }) => {
    await page.route("**/api/quick-predict", async (route) => {
      await page.waitForTimeout(200);
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          vehicle: {
            manufacturer: "Toyota",
            commercial_model: "Corolla",
            production_year: 2021,
          },
          prediction: {
            claim_probability: 0.6124,
            risk_level: "High",
            recommendation: "Manual underwriting review",
          },
          top_risk_drivers: [
            {
              title: "Policy tenure profile",
              direction: "increase",
              detail: "Longer policy tenure aligns with higher-risk portfolio patterns.",
            },
          ],
          metadata: {
            model_version: "sprint_06_final_freeze_v1",
            prediction_timestamp: "2026-06-24T12:00:00Z",
          },
        }),
      });
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.locator("#license_plate").fill("1234567");
    await page.locator("#driver_age").fill("25");
    await page.locator("#policy_tenure").fill("10");
    await page.locator("#city").fill("תל");
    await page.getByRole("option", { name: "תל אביב-יפו" }).click();
    await page.getByRole("button", { name: "בצע הערכת סיכון" }).click();

    await expect(page.locator("#analyze-button")).toHaveText("מבצע הערכת סיכון...");
    await expect(page.locator("#result-dashboard")).toBeVisible();
    await expect(page.locator("#vehicle-manufacturer")).toHaveText("Toyota");
    await expect(page.locator("#vehicle-commercial-model")).toHaveText("Corolla");
    await expect(page.locator("#claim-probability")).toHaveText("61.2%");
    await expect(page.locator("#risk-level")).toHaveText("סיכון גבוה");
    await expect(page.locator("#recommendation")).toHaveText("נדרשת בדיקה מעמיקה");
    await expect(page.locator("#top-risk-drivers .driver-item")).toHaveCount(1);
    await expect(page.locator("#technical-details")).not.toHaveAttribute("open", "");
  });

  test("empty submission shows inline validation guidance", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.getByRole("button", { name: "בצע הערכת סיכון" }).click();

    await expect(page.locator("#form-error")).toHaveText("יש להזין מספר רכב.");
  });

  test("api failure shows a business-friendly vehicle lookup error", async ({ page }) => {
    await page.route("**/api/quick-predict", async (route) => {
      await route.fulfill({
        status: 502,
        contentType: "application/json",
        body: JSON.stringify({
          detail: "vehicle registry request failed",
        }),
      });
    });

    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await page.locator("#license_plate").fill("1234567");
    await page.locator("#driver_age").fill("35");
    await page.locator("#policy_tenure").fill("10");
    await page.locator("#city").fill("תל");
    await page.getByRole("option", { name: "תל אביב-יפו" }).click();
    await page.getByRole("button", { name: "בצע הערכת סיכון" }).click();

    await expect(page.locator("#form-error")).toHaveText("לא ניתן לאתר את פרטי הרכב כעת");
    await expect(page.locator("#form-error")).not.toContainText("אירעה שגיאה בלתי צפויה");
  });
});
