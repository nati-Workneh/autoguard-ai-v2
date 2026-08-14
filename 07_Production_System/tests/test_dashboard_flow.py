from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from textwrap import dedent
from urllib import request as urllib_request

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

NODE_PLAYWRIGHT_SCRIPT = dedent(
    """
    const assert = require("node:assert/strict");
    const { chromium } = require("playwright");

    const baseUrl = process.env.BASE_URL;
    const scenario = process.env.SCENARIO;

    function delay(ms) {
      return new Promise((resolve) => setTimeout(resolve, ms));
    }

    async function run() {
      const browser = await chromium.launch({ headless: true });
      const page = await browser.newPage();

      await page.route("**/api/v2/health", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            status: "ok",
            model_loaded: true,
            model_name: "AutoGuard AI V2 Production Model",
            model_version: "v2.0.0"
          })
        });
      });

      if (scenario === "success") {
        await page.route("**/api/v2/quick-predict", async (route) => {
          await delay(250);
          await route.fulfill({
            status: 200,
            contentType: "application/json",
            body: JSON.stringify({
              vehicle: {
                manufacturer: "Toyota",
                commercial_model: "Corolla",
                production_year: 2021,
                vehicle_year_category: "after 2015"
              },
              prediction: {
                claim_probability: 0.6124,
                risk_level: "High",
                recommendation: "Manual underwriting review"
              },
              premium_impact: {
                direction: "surcharge",
                min_percent: 10.0,
                max_percent: 25.0,
                estimated_percent: 18.5,
                summary: "תוספת משוערת של 18.5% (טווח 10%-25%)"
              },
              top_risk_drivers: [
                {
                  title: "Driving experience",
                  direction: "increase",
                  detail: "Limited driving experience is the strongest contributor to higher predicted risk."
                },
                {
                  title: "Vehicle ownership",
                  direction: "increase",
                  detail: "Not privately owning the vehicle contributed to a higher risk assessment."
                }
              ],
              metadata: {
                model_version: "v2.0.0",
                model_name: "AutoGuard AI V2 Production Model",
                prediction_timestamp: "2026-06-24T12:00:00Z"
              }
            })
          });
        });
      } else {
        await page.route("**/api/v2/quick-predict", async (route) => {
          await delay(150);
          await route.fulfill({
            status: 502,
            contentType: "application/json",
            body: JSON.stringify({
              detail: "vehicle registry request failed"
            })
          });
        });
      }

      await page.goto(baseUrl, { waitUntil: "networkidle" });

      assert.match(await page.title(), /AutoGuard AI/i);
      assert.equal(await page.locator("body").evaluate((element) => element.classList.contains("app-is-gated")), true);
      await page.locator("#landing-screen").waitFor({ state: "visible" });
      assert.equal(await page.locator("#landing-video").evaluate((element) => element.autoplay), true);
      assert.equal(await page.locator("#landing-video").evaluate((element) => element.muted), true);
      assert.equal(await page.locator("#landing-video").evaluate((element) => element.loop), true);
      assert.equal(await page.locator("#landing-video").evaluate((element) => element.preload), "auto");
      assert.equal(await page.locator("#landing-video").evaluate((element) => getComputedStyle(element).objectFit), "cover");

      await page.locator("#enter-app-button").click();
      await page.waitForTimeout(820);

      assert.equal(await page.locator("body").evaluate((element) => element.classList.contains("has-entered")), true);
      assert.equal(await page.locator("#app-shell").getAttribute("aria-hidden"), null);
      await page.locator(".hero-logo-image").waitFor({ state: "visible" });
      assert.equal(await page.locator(".hero-logo-image").evaluate((element) => element.getAttribute("src")), "/assets/logo-192222.png");
      assert.equal(await page.locator(".hero-logo-image").evaluate((element) => getComputedStyle(element).objectFit), "contain");
      assert.equal(await page.locator(".hero-backdrop-panel").count(), 0);
      assert.equal(await page.locator("#quick-predict-form input[type=number], #quick-predict-form input[type=text]").count(), 7);
      assert.equal(await page.locator("#quick-predict-form input[type=radio]").count(), 3);
      assert.equal(await page.locator("#quick-predict-form select").count(), 0);
      assert.equal(await page.locator("#quick-predict-form textarea").count(), 0);
      assert.match(await page.locator("#health-label").textContent(), /המערכת פעילה/);

      await page.locator("#license_plate").fill("1234567");
      await page.locator("#age").fill("25");
      await page.locator("#driving_experience_years").fill("3");
      await page.locator("#past_accidents").fill("1");
      await page.locator("#speeding_violations").fill("2");
      await page.locator("#duis").fill("0");
      await page.locator("#annual_mileage").fill("18000");
      await page.locator('input[name="vehicle_ownership"][value="leasing"]').check({ force: true });
      await page.locator("#analyze-button").click();

      await page.waitForTimeout(40);
      assert.equal(await page.locator("#analyze-button").textContent(), "מבצע הערכת סיכון...");
      assert.equal(await page.locator("#analyze-button").isDisabled(), true);
      assert.match(await page.locator("#form-status").textContent(), /מבצע הערכת סיכון/);

      if (scenario === "success") {
        await page.locator("#result-dashboard").waitFor({ state: "visible" });
        assert.equal(await page.locator("#vehicle-manufacturer").textContent(), "Toyota");
        assert.equal(await page.locator("#vehicle-commercial-model").textContent(), "Corolla");
        assert.equal(await page.locator("#vehicle-production-year").textContent(), "2021");
        assert.equal(await page.locator("#claim-probability").textContent(), "61.2%");
        assert.equal(await page.locator("#risk-level").textContent(), "סיכון גבוה");
        assert.equal(await page.locator("#recommendation").textContent(), "נדרשת בדיקה מעמיקה");
        assert.equal(await page.locator("#top-risk-drivers .driver-item").count(), 2);
        assert.equal(await page.locator("#technical-details").evaluate((element) => element.open), false);
        assert.match(await page.locator("#form-status").textContent(), /הושלמה בהצלחה/);
      } else {
        await page.locator("#form-error").waitFor({ state: "visible" });
        assert.equal(await page.locator("#form-error").textContent(), "לא ניתן לאתר את פרטי הרכב כעת");
        assert.equal(await page.locator("#result-empty").isVisible(), true);
        assert.equal(await page.locator("#result-dashboard").isHidden(), true);
      }

      await browser.close();
    }

    run().catch((error) => {
      console.error(error);
      process.exit(1);
    });
    """
)


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(base_url: str, timeout_seconds: float = 30.0) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urllib_request.urlopen(f"{base_url}/", timeout=2) as response:
                if response.status == 200:
                    return
        except Exception as exc:  # pragma: no cover - retry loop
            last_error = exc
            time.sleep(0.25)

    raise RuntimeError(f"dashboard server did not become ready: {last_error}")


@pytest.fixture(scope="module")
def dashboard_server() -> str:
    port = _find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        _wait_for_server(base_url)
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def _run_browser_scenario(base_url: str, scenario: str) -> None:
    env = os.environ.copy()
    env.update(
        {
            "BASE_URL": base_url,
            "SCENARIO": scenario,
        }
    )
    subprocess.run(
        ["node", "-e", NODE_PLAYWRIGHT_SCRIPT],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def test_dashboard_flow_renders_successful_prediction(dashboard_server: str) -> None:
    _run_browser_scenario(dashboard_server, "success")


def test_dashboard_flow_handles_api_failure(dashboard_server: str) -> None:
    _run_browser_scenario(dashboard_server, "api_failure")


# ---------------------------------------------------------------------------
# Sprint 10.7 -- missing vehicle_ownership is caught client-side, never sent
# ---------------------------------------------------------------------------

MISSING_OWNERSHIP_SCRIPT = dedent(
    """
    const assert = require("node:assert/strict");
    const { chromium } = require("playwright");

    const baseUrl = process.env.BASE_URL;

    async function run() {
      const browser = await chromium.launch({ headless: true });
      const page = await browser.newPage();

      await page.route("**/api/v2/health", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ status: "ok", model_loaded: true, model_name: "x", model_version: "v2.0.0" })
        });
      });

      let predictCalled = false;
      await page.route("**/api/v2/quick-predict", async (route) => {
        predictCalled = true;
        await route.fulfill({ status: 200, contentType: "application/json", body: "{}" });
      });

      await page.goto(baseUrl, { waitUntil: "networkidle" });
      await page.locator("#enter-app-button").click();
      await page.waitForTimeout(820);

      await page.locator("#license_plate").fill("1234567");
      await page.locator("#age").fill("25");
      await page.locator("#driving_experience_years").fill("3");
      await page.locator("#past_accidents").fill("0");
      await page.locator("#speeding_violations").fill("0");
      await page.locator("#duis").fill("0");
      await page.locator("#annual_mileage").fill("18000");
      // vehicle_ownership intentionally left unselected.
      await page.locator("#analyze-button").click();

      await page.waitForTimeout(40);
      assert.equal(predictCalled, false, "quick-predict must not be called without vehicle_ownership");
      assert.equal(await page.locator("#form-error").isVisible(), true);
      assert.match(await page.locator("#form-error").textContent(), /בעלות/);

      await browser.close();
    }

    run().catch((error) => {
      console.error(error);
      process.exit(1);
    });
    """
)


def test_dashboard_flow_blocks_submission_without_vehicle_ownership(dashboard_server: str) -> None:
    env = os.environ.copy()
    env["BASE_URL"] = dashboard_server
    subprocess.run(
        ["node", "-e", MISSING_OWNERSHIP_SCRIPT],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
