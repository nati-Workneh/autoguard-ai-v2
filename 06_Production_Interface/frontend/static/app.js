const bodyEl = document.body;
const appShellEl = document.getElementById("app-shell");
const landingScreenEl = document.getElementById("landing-screen");
const landingVideoEl = document.getElementById("landing-video");
const enterAppButton = document.getElementById("enter-app-button");
const healthChip = document.getElementById("health-chip");
const healthLabel = document.getElementById("health-label");
const form = document.getElementById("quick-predict-form");
const formErrorEl = document.getElementById("form-error");
const formStatusEl = document.getElementById("form-status");
const analyzeButton = document.getElementById("analyze-button");
const clearButton = document.getElementById("clear-button");
const resultEmptyEl = document.getElementById("result-empty");
const resultDashboardEl = document.getElementById("result-dashboard");
const technicalDetailsEl = document.getElementById("technical-details");
const vehiclePlateEl = document.getElementById("vehicle-plate");
const vehicleTitleEl = document.getElementById("vehicle-title");
const vehicleManufacturerEl = document.getElementById("vehicle-manufacturer");
const vehicleCommercialModelEl = document.getElementById("vehicle-commercial-model");
const vehicleProductionYearEl = document.getElementById("vehicle-production-year");
const vehicleYearDetailEl = document.getElementById("vehicle-year-detail");
const claimProbabilityEl = document.getElementById("claim-probability");
const riskScoreEl = document.getElementById("risk-score");
const riskBadgeEl = document.getElementById("risk-badge");
const riskLevelEl = document.getElementById("risk-level");
const riskCopyEl = document.getElementById("risk-copy");
const recommendationEl = document.getElementById("recommendation");
const premiumImpactSummaryEl = document.getElementById("premium-impact-summary");
const riskDriversEl = document.getElementById("top-risk-drivers");
const modelVersionEl = document.getElementById("model-version");
const predictionTimestampEl = document.getElementById("prediction-timestamp");

const licensePlateInput = document.getElementById("license_plate");
const ageInput = document.getElementById("age");
const drivingExperienceInput = document.getElementById("driving_experience_years");
const pastAccidentsInput = document.getElementById("past_accidents");
const speedingViolationsInput = document.getElementById("speeding_violations");
const duisInput = document.getElementById("duis");
const annualMileageInput = document.getElementById("annual_mileage");
const ownershipInputs = Array.from(form.querySelectorAll('input[name="vehicle_ownership"]'));

const emptyTitleSelector = ".empty-title";
const emptyCopySelector = ".empty-copy";

const formControls = Array.from(form.querySelectorAll("input, button"));
const prefersReducedMotionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
const LANDING_TRANSITION_MS = 760;

let landingTransitionTimer = null;

const NUMERIC_FIELDS = [
  { input: ageInput, key: "age", min: 18, max: 100 },
  { input: drivingExperienceInput, key: "driving_experience_years", min: 0, max: 80 },
  { input: pastAccidentsInput, key: "past_accidents", min: 0, max: 50 },
  { input: speedingViolationsInput, key: "speeding_violations", min: 0, max: 100 },
  { input: duisInput, key: "duis", min: 0, max: 20 },
  { input: annualMileageInput, key: "annual_mileage", min: 1, max: 200000 },
];

const UI_TEXT = {
  analyzeRisk: "בצע הערכת סיכון",
  analyzingRisk: "מבצע הערכת סיכון...",
  healthChecking: "טוען נתונים...",
  healthReady: "המערכת פעילה",
  healthUnavailable: "המערכת אינה זמינה",
  platePending: "ממתין למספר רכב",
  vehiclePending: "פרטי הרכב יוצגו לאחר האיתור",
  emptyTitle: "המערכת מוכנה לביצוע הערכת סיכון",
  emptyCopy: "יש להזין מספר רכב ולהשלים את שאלון הנהג כדי להפיק הערכת סיכון.",
  loadingTitle: "מבצע הערכת סיכון...",
  loadingCopy: "מאתר פרטי רכב ומחשב את הערכת הסיכון.",
  successStatus: "הערכת הסיכון הושלמה בהצלחה.",
  successRecommendation: "מומלץ לבדיקה נוספת",
  premiumImpactStandard: "פרמיה סטנדרטית, ללא שינוי משוער",
  analysisUnavailableTitle: "לא ניתן להשלים את הערכת הסיכון כעת.",
  analysisUnavailableCopy: "יש לבדוק את הנתונים שהוזנו או לנסות שוב בעוד מספר רגעים.",
  networkFailure: "לא ניתן להשלים את הערכת הסיכון כעת.",
  validationMissing: "יש להשלים את כל שדות החובה לפני ביצוע הערכת הסיכון.",
  recommendationUnavailable: "המלצת המערכת אינה זמינה",
  driverPlaceholder: "הגורמים המשפיעים על התוצאה יוצגו כאן לאחר השלמת הבדיקה.",
  invalidLicensePlate: "מספר רכב לא תקין",
  vehicleNotFound: "לא נמצא רכב התואם למספר שהוזן.",
  predictionFailed: "לא ניתן להשלים את הערכת הסיכון כעת.",
  ageValidation: "גיל הנהג חייב להיות בין 18 ל-100",
  experienceValidation: "שנות הנהיגה חייבות להיות בין 0 ל-80, ולא לעלות על גיל הנהג פחות 16",
  pastAccidentsValidation: "מספר התאונות בעבר חייב להיות 0 ומעלה",
  speedingViolationsValidation: "מספר דוחות המהירות חייב להיות 0 ומעלה",
  duisValidation: "מספר עבירות הנהיגה בשכרות חייב להיות 0 ומעלה",
  annualMileageValidation: "יש להזין קילומטראז' שנתי חיובי",
  ownershipRequired: "יש לבחור סוג בעלות על הרכב",
};

const FIELD_LABELS = {
  license_plate: "מספר רכב",
  age: "גיל הנהג",
  driving_experience_years: "שנות נהיגה",
  past_accidents: "מספר תאונות בעבר",
  speeding_violations: "דוחות מהירות",
  duis: "עבירות נהיגה בשכרות",
  annual_mileage: "קילומטראז' שנתי",
  vehicle_ownership: "בעלות על הרכב",
  field: "שדה",
};

const RISK_PRESENTATION = {
  Low: {
    badgeClass: "risk-low",
    label: "סיכון נמוך",
    copy: "הפרופיל שנבדק מתאים למסלול חיתום שגרתי ללא צורך בהסלמה מיוחדת.",
  },
  Medium: {
    badgeClass: "risk-medium",
    label: "סיכון בינוני",
    copy: "הפרופיל שנבחן מצביע על צורך במסלול בדיקה חיתומית ברמת עדיפות בינונית.",
  },
  High: {
    badgeClass: "risk-high",
    label: "סיכון גבוה",
    copy: "הפרופיל שנבחן מחייב העברה לבדיקה חיתומית מעמיקה יותר.",
  },
};

const RECOMMENDATION_TRANSLATIONS = {
  "Standard approval": "מומלץ לאישור",
  "Additional underwriting review": "מומלץ לבדיקה נוספת",
  "Manual underwriting review": "נדרשת בדיקה מעמיקה",
};

const DRIVER_TITLE_TRANSLATIONS = {
  "Driver age bracket": "טווח גיל הנהג",
  "Driving experience": "שנות נהיגה",
  "Vehicle year": "שנת ייצור הרכב",
  "Annual mileage": "קילומטראז' שנתי",
  "Past accidents": "תאונות בעבר",
  "Speeding violations": "דוחות מהירות",
  "DUI history": "עבירות נהיגה בשכרות",
  "Vehicle ownership": "בעלות על הרכב",
};

const DRIVER_DETAIL_TRANSLATIONS = {
  "This driver's age bracket is associated with higher claim risk in the model.":
    "טווח הגיל של הנהג נקשר לסיכון גבוה יותר להגשת תביעה במודל.",
  "This driver's age bracket is associated with lower claim risk in the model.":
    "טווח הגיל של הנהג נקשר לסיכון נמוך יותר להגשת תביעה במודל.",
  "Limited driving experience is the strongest contributor to higher predicted risk.":
    "מספר שנות הנהיגה המוגבל הוא הגורם המשפיע ביותר על הערכת סיכון גבוהה.",
  "Extensive driving experience is the strongest contributor to lower predicted risk.":
    "ניסיון הנהיגה הרב הוא הגורם המשפיע ביותר על הערכת סיכון נמוכה.",
  "An older vehicle (before 2015) contributed to a higher risk assessment.":
    "רכב ישן יותר (לפני 2015) תרם להערכת סיכון גבוהה יותר.",
  "A newer vehicle (after 2015) contributed to a lower risk assessment.":
    "רכב חדש יותר (אחרי 2015) תרם להערכת סיכון נמוכה יותר.",
  "Higher annual mileage contributed to a higher risk assessment.":
    "קילומטראז' שנתי גבוה תרם להערכת סיכון גבוהה יותר.",
  "Lower annual mileage contributed to a lower risk assessment.":
    "קילומטראז' שנתי נמוך תרם להערכת סיכון נמוכה יותר.",
  "Past accident history contributed to a higher risk assessment.":
    "היסטוריית תאונות עבר תרמה להערכת סיכון גבוהה יותר.",
  "Past accident history did not push the risk assessment higher, given this driver's profile.":
    "היסטוריית תאונות העבר לא העלתה את הערכת הסיכון, בהינתן פרופיל הנהג הנוכחי.",
  "Speeding violation history contributed to a higher risk assessment.":
    "היסטוריית דוחות מהירות תרמה להערכת סיכון גבוהה יותר.",
  "Speeding violation history contributed to a lower risk assessment.":
    "היסטוריית דוחות מהירות תרמה להערכת סיכון נמוכה יותר.",
  "DUI history contributed to a higher risk assessment.":
    "היסטוריית עבירות נהיגה בשכרות תרמה להערכת סיכון גבוהה יותר.",
  "DUI history did not push the risk assessment higher, given this driver's profile.":
    "היסטוריית עבירות הנהיגה בשכרות לא העלתה את הערכת הסיכון, בהינתן פרופיל הנהג הנוכחי.",
  "Not privately owning the vehicle contributed to a higher risk assessment.":
    "היעדר בעלות פרטית על הרכב (ליסינג/רכב חברה) תרם להערכת סיכון גבוהה יותר.",
  "Privately owning the vehicle contributed to a lower risk assessment.":
    "בעלות פרטית על הרכב תרמה להערכת סיכון נמוכה יותר.",
};

function fetchJson(url, options = {}) {
  return fetch(url, options).then(async (response) => {
    const contentType = response.headers.get("content-type") || "";
    let body = null;

    if (contentType.includes("application/json")) {
      body = await response.json();
    } else {
      const rawText = await response.text();
      body = rawText ? { detail: rawText } : null;
    }

    return { response, body };
  });
}

function showFormError(message) {
  formErrorEl.hidden = false;
  formErrorEl.textContent = message;
}

function clearFormError() {
  formErrorEl.hidden = true;
  formErrorEl.textContent = "";
}

function showFormStatus(message) {
  formStatusEl.hidden = false;
  formStatusEl.textContent = message;
}

function clearFormStatus() {
  formStatusEl.hidden = true;
  formStatusEl.textContent = "";
}

function setBusy(isBusy) {
  formControls.forEach((control) => {
    control.disabled = isBusy;
  });

  analyzeButton.textContent = isBusy ? UI_TEXT.analyzingRisk : UI_TEXT.analyzeRisk;
  resultEmptyEl.classList.toggle("is-busy", isBusy);
}

function setAppShellInteractive(isInteractive) {
  if (!appShellEl) {
    return;
  }

  if (isInteractive) {
    appShellEl.removeAttribute("inert");
    appShellEl.removeAttribute("aria-hidden");
    return;
  }

  appShellEl.setAttribute("inert", "");
  appShellEl.setAttribute("aria-hidden", "true");
}

function syncReducedMotionPreference() {
  const prefersReducedMotion = prefersReducedMotionQuery.matches;
  bodyEl.classList.toggle("prefers-reduced-motion", prefersReducedMotion);

  if (!landingVideoEl) {
    return;
  }

  if (prefersReducedMotion) {
    landingVideoEl.pause();
    return;
  }

  landingVideoEl.muted = true;
  landingVideoEl.play().catch(() => {});
}

function setHealthStatus(health) {
  const online = Boolean(health?.status === "ok");
  healthChip.classList.toggle("is-online", online);
  healthChip.classList.toggle("is-offline", !online);
  healthLabel.textContent = online ? UI_TEXT.healthReady : UI_TEXT.healthUnavailable;
}

function setEmptyState(title, copy) {
  const titleEl = resultEmptyEl.querySelector(emptyTitleSelector);
  const copyEl = resultEmptyEl.querySelector(emptyCopySelector);
  titleEl.textContent = title;
  copyEl.textContent = copy;
  resultEmptyEl.hidden = false;
  resultDashboardEl.hidden = true;
}

function resetDashboard() {
  technicalDetailsEl.open = false;
  vehiclePlateEl.textContent = UI_TEXT.platePending;
  vehicleTitleEl.textContent = UI_TEXT.vehiclePending;
  vehicleManufacturerEl.textContent = "-";
  vehicleCommercialModelEl.textContent = "-";
  vehicleProductionYearEl.textContent = "-";
  vehicleYearDetailEl.textContent = "-";
  claimProbabilityEl.textContent = "0%";
  riskScoreEl.textContent = "0";
  recommendationEl.textContent = UI_TEXT.successRecommendation;
  setPremiumImpactPresentation(null);
  modelVersionEl.textContent = "-";
  predictionTimestampEl.textContent = "-";
  setRiskPresentation("Medium");
  renderRiskDrivers([]);
  setEmptyState(UI_TEXT.emptyTitle, UI_TEXT.emptyCopy);
}

function completeLandingEntry() {
  bodyEl.classList.remove("app-is-gated");

  if (landingScreenEl) {
    landingScreenEl.hidden = true;
  }

  window.scrollTo({ top: 0, behavior: "auto" });
  licensePlateInput.focus({ preventScroll: true });
}

function enterApplication() {
  if (bodyEl.classList.contains("has-entered")) {
    return;
  }

  bodyEl.classList.add("has-entered");
  setAppShellInteractive(true);

  if (enterAppButton) {
    enterAppButton.disabled = true;
  }

  if (landingScreenEl) {
    landingScreenEl.setAttribute("aria-hidden", "true");
  }

  if (landingTransitionTimer) {
    window.clearTimeout(landingTransitionTimer);
  }

  const transitionMs = prefersReducedMotionQuery.matches ? 0 : LANDING_TRANSITION_MS;
  if (transitionMs === 0) {
    completeLandingEntry();
    return;
  }

  landingTransitionTimer = window.setTimeout(() => {
    completeLandingEntry();
    landingTransitionTimer = null;
  }, transitionMs);
}

function normalizeText(value) {
  return String(value || "").trim();
}

function sanitizeLicensePlate(value) {
  return String(value || "").replace(/\D/g, "");
}

function getSelectedOwnership() {
  const checked = ownershipInputs.find((input) => input.checked);
  return checked ? checked.value : "";
}

function buildPayload() {
  const formData = new FormData(form);

  return {
    license_plate: sanitizeLicensePlate(formData.get("license_plate")),
    age: Number(formData.get("age")),
    driving_experience_years: Number(formData.get("driving_experience_years")),
    past_accidents: Number(formData.get("past_accidents")),
    speeding_violations: Number(formData.get("speeding_violations")),
    duis: Number(formData.get("duis")),
    annual_mileage: Number(formData.get("annual_mileage")),
    vehicle_ownership: getSelectedOwnership(),
  };
}

function translateFieldLabel(fieldName) {
  return FIELD_LABELS[fieldName] || FIELD_LABELS.field;
}

const FIELD_VALIDATION_MESSAGES = {
  license_plate: () => UI_TEXT.invalidLicensePlate,
  age: () => UI_TEXT.ageValidation,
  driving_experience_years: () => UI_TEXT.experienceValidation,
  past_accidents: () => UI_TEXT.pastAccidentsValidation,
  speeding_violations: () => UI_TEXT.speedingViolationsValidation,
  duis: () => UI_TEXT.duisValidation,
  annual_mileage: () => UI_TEXT.annualMileageValidation,
  vehicle_ownership: () => UI_TEXT.ownershipRequired,
};

function translateValidationMessage(message, fieldName) {
  const normalizedMessage = String(message || "");
  const knownField = FIELD_VALIDATION_MESSAGES[fieldName];
  if (knownField) {
    return knownField();
  }
  if (/field required/i.test(normalizedMessage) || /value must not be empty/i.test(normalizedMessage)) {
    return "יש להשלים שדה זה.";
  }
  if (/valid number/i.test(normalizedMessage) || /must be numeric/i.test(normalizedMessage)) {
    return "יש להזין ערך מספרי תקין.";
  }
  return UI_TEXT.predictionFailed;
}

function translateServerDetail(detail) {
  const normalizedDetail = String(detail || "");

  if (/vehicle not found/i.test(normalizedDetail)) {
    return UI_TEXT.vehicleNotFound;
  }
  if (/license_plate/i.test(normalizedDetail) && /(7 or 8 digits|invalid)/i.test(normalizedDetail)) {
    return UI_TEXT.invalidLicensePlate;
  }
  if (/vehicle registry request failed|upstream|missing manufacturer|missing commercial model|missing production year|invalid json|unsuccessful response|response missing/i.test(normalizedDetail)) {
    return "לא ניתן לאתר את פרטי הרכב כעת";
  }
  if (/timed out/i.test(normalizedDetail)) {
    return "איתור פרטי הרכב מתעכב, נסו שוב בעוד רגע";
  }
  if (/vehicle_ownership/i.test(normalizedDetail)) {
    return UI_TEXT.ownershipRequired;
  }
  if (/age/i.test(normalizedDetail)) {
    return UI_TEXT.ageValidation;
  }
  if (/driving_experience_years/i.test(normalizedDetail)) {
    return UI_TEXT.experienceValidation;
  }
  if (/could not be processed|unexpected response|request could not be processed|failed|predict/i.test(normalizedDetail)) {
    return UI_TEXT.predictionFailed;
  }

  return UI_TEXT.predictionFailed;
}

function formatApiError(body) {
  if (!body) {
    return UI_TEXT.predictionFailed;
  }

  if (typeof body.detail === "string") {
    return translateServerDetail(body.detail);
  }

  if (Array.isArray(body.detail) && body.detail.length > 0) {
    return body.detail
      .map((item) => {
        const locParts = Array.isArray(item.loc) ? item.loc.slice(1) : ["field"];
        const fieldName = String(locParts[0] || "field");
        return `${translateFieldLabel(fieldName)}: ${translateValidationMessage(item.msg, fieldName)}`;
      })
      .join(" · ");
  }

  return UI_TEXT.predictionFailed;
}

function formatProbability(probability) {
  const percent = Number(probability) * 100;
  if (Number.isNaN(percent)) {
    return "-";
  }

  const rounded = Math.round(percent * 10) / 10;
  return `${Number.isInteger(rounded) ? rounded.toFixed(0) : rounded.toFixed(1)}%`;
}

/** Presentation-only 0-100 risk score derived from the existing claim_probability
 * the API already returns. No new backend field or model output is introduced. */
function formatRiskScore(probability) {
  const score = Math.round(Number(probability) * 100);
  return Number.isFinite(score) ? String(Math.min(100, Math.max(0, score))) : "0";
}

function formatPlateForDisplay(value) {
  const digits = sanitizeLicensePlate(value);
  if (digits.length === 7) {
    return `${digits.slice(0, 2)}-${digits.slice(2, 5)}-${digits.slice(5)}`;
  }
  if (digits.length === 8) {
    return `${digits.slice(0, 3)}-${digits.slice(3, 5)}-${digits.slice(5)}`;
  }
  return normalizeText(value) || UI_TEXT.platePending;
}

function formatTimestamp(timestamp) {
  try {
    return new Intl.DateTimeFormat("he-IL", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(timestamp));
  } catch (error) {
    return String(timestamp);
  }
}

function setRiskPresentation(riskLevel) {
  const presentation = RISK_PRESENTATION[riskLevel] || RISK_PRESENTATION.Medium;
  riskBadgeEl.className = `risk-badge ${presentation.badgeClass}`;
  riskLevelEl.textContent = presentation.label;
  riskCopyEl.textContent = presentation.copy;
}

function translateRecommendation(recommendation, riskLevel) {
  const normalizedRecommendation = String(recommendation || "").trim();
  if (RECOMMENDATION_TRANSLATIONS[normalizedRecommendation]) {
    return RECOMMENDATION_TRANSLATIONS[normalizedRecommendation];
  }

  if (riskLevel === "High") {
    return "נדרשת בדיקת חתם בכיר";
  }
  if (riskLevel === "Low") {
    return "מומלץ לאישור";
  }
  return UI_TEXT.successRecommendation;
}

function buildDriverFallback(detailDirection) {
  if (detailDirection === "increase") {
    return {
      title: "גורם סיכון מרכזי",
      detail: "הנתון שנבחן מחזק את הצורך בבדיקה חיתומית מעמיקה יותר.",
    };
  }

  return {
    title: "גורם ממתן סיכון",
    detail: "הנתון שנבחן תומך בהערכת סיכון מתונה יותר.",
  };
}

function translateDriver(driver) {
  const direction = driver.direction === "increase" ? "increase" : "decrease";
  const fallback = buildDriverFallback(direction);

  return {
    title: DRIVER_TITLE_TRANSLATIONS[driver.title] || fallback.title,
    direction,
    detail: DRIVER_DETAIL_TRANSLATIONS[driver.detail] || fallback.detail,
  };
}

function renderRiskDrivers(drivers) {
  riskDriversEl.innerHTML = "";

  if (!Array.isArray(drivers) || drivers.length === 0) {
    const placeholder = document.createElement("li");
    placeholder.className = "driver-placeholder result-span-full";
    placeholder.textContent = UI_TEXT.driverPlaceholder;
    riskDriversEl.appendChild(placeholder);
    return;
  }

  drivers.forEach((driver) => {
    const translatedDriver = translateDriver(driver);
    const item = document.createElement("li");
    item.className = "driver-item";

    const header = document.createElement("div");
    header.className = "driver-item-header";

    const title = document.createElement("p");
    title.className = "driver-title";
    title.textContent = translatedDriver.title;

    const direction = document.createElement("span");
    const directionIncrease = translatedDriver.direction === "increase";
    direction.className = `driver-direction ${directionIncrease ? "is-increase" : "is-decrease"}`;
    direction.textContent = directionIncrease ? "מעלה סיכון" : "מפחית סיכון";

    const detail = document.createElement("p");
    detail.className = "driver-detail";
    detail.textContent = translatedDriver.detail;

    header.append(title, direction);
    item.append(header, detail);
    riskDriversEl.appendChild(item);
  });
}

function setPremiumImpactPresentation(premiumImpact) {
  const directionClasses = ["premium-impact-discount", "premium-impact-surcharge", "premium-impact-standard"];
  premiumImpactSummaryEl.classList.remove(...directionClasses);

  if (!premiumImpact) {
    premiumImpactSummaryEl.textContent = UI_TEXT.premiumImpactStandard;
    premiumImpactSummaryEl.classList.add("premium-impact-standard");
    return;
  }

  premiumImpactSummaryEl.textContent = premiumImpact.summary || UI_TEXT.premiumImpactStandard;
  premiumImpactSummaryEl.classList.add(`premium-impact-${premiumImpact.direction}`);
}

function renderDashboard(payload, result) {
  const vehicle = result.vehicle || {};
  const prediction = result.prediction || {};
  const metadata = result.metadata || {};
  const vehicleTitle = `${vehicle.manufacturer || ""} ${vehicle.commercial_model || ""}`.trim();

  vehiclePlateEl.textContent = formatPlateForDisplay(payload.license_plate);
  vehicleTitleEl.textContent = vehicleTitle || UI_TEXT.vehiclePending;
  vehicleManufacturerEl.textContent = vehicle.manufacturer || "-";
  vehicleCommercialModelEl.textContent = vehicle.commercial_model || "-";
  vehicleProductionYearEl.textContent = vehicle.production_year || "-";
  vehicleYearDetailEl.textContent = vehicle.production_year || "-";

  claimProbabilityEl.textContent = formatProbability(prediction.claim_probability);
  riskScoreEl.textContent = formatRiskScore(prediction.claim_probability);
  setRiskPresentation(prediction.risk_level);
  // Risk band is presentation-only; the backend policy supplies routing.
  recommendationEl.textContent = prediction.business_action || translateRecommendation(prediction.recommendation, prediction.risk_level);
  setPremiumImpactPresentation(result.premium_impact);
  modelVersionEl.textContent = metadata.model_version || "-";
  predictionTimestampEl.textContent = metadata.prediction_timestamp
    ? formatTimestamp(metadata.prediction_timestamp)
    : "-";
  renderRiskDrivers(result.top_risk_drivers);

  technicalDetailsEl.open = false;
  resultEmptyEl.hidden = true;
  resultDashboardEl.hidden = false;
}

function validatePayload(payload) {
  const errors = [];
  const licensePlateError = !payload.license_plate
    ? "יש להזין מספר רכב."
    : payload.license_plate.length === 7 || payload.license_plate.length === 8
      ? ""
      : UI_TEXT.invalidLicensePlate;

  licensePlateInput.setCustomValidity(licensePlateError);
  errors.push(licensePlateError);

  NUMERIC_FIELDS.forEach(({ input, key, min, max }) => {
    const value = payload[key];
    const message = FIELD_VALIDATION_MESSAGES[key]();
    const error = !Number.isFinite(value)
      ? message
      : value < min || value > max
        ? message
        : "";
    input.setCustomValidity(error);
    errors.push(error);
  });

  if (Number.isFinite(payload.driving_experience_years) && Number.isFinite(payload.age)) {
    if (payload.driving_experience_years > payload.age - 16) {
      drivingExperienceInput.setCustomValidity(UI_TEXT.experienceValidation);
      errors.push(UI_TEXT.experienceValidation);
    }
  }

  const ownershipError = payload.vehicle_ownership ? "" : UI_TEXT.ownershipRequired;
  errors.push(ownershipError);

  return {
    valid: errors.every((error) => !error),
    message: errors.find((error) => error) || "",
  };
}

async function submitQuickPredict(event) {
  if (event) {
    event.preventDefault();
  }

  clearFormError();
  clearFormStatus();

  const payload = buildPayload();
  const validation = validatePayload(payload);
  if (!validation.valid) {
    showFormError(validation.message || UI_TEXT.validationMissing);
    form.reportValidity();
    return;
  }

  setBusy(true);
  showFormStatus(UI_TEXT.analyzingRisk);
  setEmptyState(UI_TEXT.loadingTitle, UI_TEXT.loadingCopy);

  try {
    const { response, body } = await fetchJson("/api/v2/quick-predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      showFormError(formatApiError(body));
      setEmptyState(UI_TEXT.analysisUnavailableTitle, UI_TEXT.analysisUnavailableCopy);
      return;
    }

    renderDashboard(payload, body);
    showFormStatus(UI_TEXT.successStatus);
  } catch (error) {
    showFormError(UI_TEXT.networkFailure);
    setEmptyState(UI_TEXT.analysisUnavailableTitle, UI_TEXT.analysisUnavailableCopy);
  } finally {
    setBusy(false);
  }
}

function clearWorkflow() {
  form.reset();
  licensePlateInput.setCustomValidity("");
  NUMERIC_FIELDS.forEach(({ input }) => input.setCustomValidity(""));
  clearFormError();
  clearFormStatus();
  resetDashboard();
}

async function initializeHealth() {
  try {
    const { response, body } = await fetchJson("/api/v2/health");
    if (!response.ok) {
      throw new Error("health check failed");
    }
    setHealthStatus(body);
  } catch (error) {
    setHealthStatus(null);
  }
}

function renderInitialState() {
  healthLabel.textContent = UI_TEXT.healthChecking;
  resetDashboard();
}

function initializeLanding() {
  if (!landingScreenEl || !appShellEl) {
    bodyEl.classList.add("has-entered");
    bodyEl.classList.remove("app-is-gated");
    setAppShellInteractive(true);
    return;
  }

  setAppShellInteractive(false);
  syncReducedMotionPreference();
}

function bindEvents() {
  enterAppButton?.addEventListener("click", enterApplication);
  form.addEventListener("submit", submitQuickPredict);
  clearButton.addEventListener("click", clearWorkflow);
  prefersReducedMotionQuery.addEventListener("change", syncReducedMotionPreference);

  [licensePlateInput, ...NUMERIC_FIELDS.map(({ input }) => input)].forEach((input) => {
    input.addEventListener("input", () => {
      input.setCustomValidity("");
      clearFormError();
    });
  });

  ownershipInputs.forEach((input) => {
    input.addEventListener("change", () => {
      clearFormError();
    });
  });
}

function initializeScrollReveal() {
  const sections = document.querySelectorAll(".fade-in-section");
  if (!sections.length) {
    return;
  }

  if (!("IntersectionObserver" in window)) {
    sections.forEach((section) => section.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  sections.forEach((section) => observer.observe(section));
}

async function initialize() {
  renderInitialState();
  initializeLanding();
  bindEvents();
  initializeScrollReveal();
  await initializeHealth();
}

void initialize();

window.AutoGuardDashboard = {
  buildPayload,
  formatApiError,
  formatPlateForDisplay,
  formatProbability,
  formatTimestamp,
  renderRiskDrivers,
  setRiskPresentation,
  translateRecommendation,
  translateServerDetail,
  validatePayload,
};
