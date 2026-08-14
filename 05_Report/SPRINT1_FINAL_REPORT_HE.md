# AutoGuard AI — דוח סיכום מלא לספרינט 1

**נושא הספרינט:** מתודולוגיית ML, בידוד נתונים ומניעת Data Leakage  
**גרסת מודל פעילה:** `v3.1.0-sprint1`  
**מועד הרצה:** 2026-08-13  
**סטטוס:** הושלם ואומת

## 1. מטרת הספרינט

מטרת Sprint 1 הייתה לתקן את ארכיטקטורת ההערכה של מודל החיזוי כך שתהיה תקינה אקדמית, ניתנת לשחזור ומוגנת מפני זליגת מידע. המטרה אינה לשפר את הציון באופן מלאכותי, אלא להבטיח שערכת המבחן אינה משפיעה על אימון, השוואת מודלים או בחירת המודל.

הארכיטקטורה שיושמה היא:

```text
מקור נתונים אמיתי
   -> Real Train
   -> Real Validation
   -> Real Test

Real Train בלבד
   -> יצירת נתוני אימון נוספים
   -> Training Pool

Training Pool -> אימון מועמדים
Real Validation -> השוואה ובחירת מודל
Real Test -> הערכה סופית אחת בלבד
```

## 2. שמירת הפרויקט המקורי

הפרויקט המקורי לא נדרס. כל השינויים בוצעו בעותק עבודה עצמאי:

`C:\Users\97252\Desktop\ML CARS project\AutoGuard_AI_Sprint1`

נוצר גם קובץ מסירה:

`C:\Users\97252\Desktop\ML CARS project\AutoGuard_AI_Sprint1.zip`

## 3. מקור הנתונים הסמכותי

מקור הנתונים האמיתי שנבחר הוא:

`02_Data/raw/Car_Insurance_Claim.csv`

מאפייניו:

- 10,000 תצפיות אמיתיות ו-19 עמודות.
- משתנה מטרה: `OUTCOME` — תביעת ביטוח (`1`) או ללא תביעה (`0`).
- מזהה טכני: `ID`.
- 17 עמודות מקור משמעותיות נוספות שימשו לבניית fingerprint של רשומה.
- לא נמצאו שורות כפולות מלאות במקור.
- נמצאו ערכים חסרים, בעיקר בשדות כגון `CREDIT_SCORE` ו-`ANNUAL_MILEAGE`; הם אינם מוסרים ידנית.
- התפלגות היעד במקור: 6,867 ללא תביעה ו-3,133 תביעות.

קובץ ה-50,000 שורות אינו משמש כמקור להפרדת ה-Validation וה-Test, מפני שהוא מכיל נתונים נוספים שנוצרו בעבר. הוא נשמר לצורכי עקיבות בלבד.

## 4. חלוקת הנתונים האמיתיים

החלוקה מתבצעת לפני יצירת נתונים נוספים, תוך שימוש ב-seed קבוע `42` ובחלוקה קבוצתית-שכבתית (`StratifiedGroupKFold`).

| מחיצה | מספר שורות | תפקיד |
|---|---:|---|
| Real Train | 6,400 | אימון בסיסי ויצירת נתוני אימון נוספים |
| Real Validation | 1,599 | השוואת מועמדים ובחירת מודל בלבד |
| Real Test | 2,001 | הערכה סופית אחת בלבד |

הפרש של רשומה אחת מהיעדים התאורטיים 6,400/1,600/2,000 נובע משמירת קבוצות fingerprint שלמות יחד. זהו מחיר קטן ונכון מתודולוגית לשם מניעת duplicate leakage.

## 5. מניעת דליפת כפילויות

לכל רשומה נוצר content fingerprint מכל מאפייני המקור המשמעותיים, ללא `ID`, ללא `OUTCOME` וללא עמודות טכניות שנוצרות בתהליך. כך רשומות זהות מבחינת תוכן נשארות באותה מחיצה, גם אם מזהי ה-ID שלהן שונים.

בדיקות ה-leakage הממומשות כ-assertions החזירו:

| השוואה | חפיפת IDs | חפיפת fingerprints |
|---|---:|---:|
| Real Train / Real Validation | 0 | 0 |
| Real Train / Real Test | 0 | 0 |
| Real Validation / Real Test | 0 | 0 |
| Training Pool / Real Validation | 0 | 0 |
| Training Pool / Real Test | 0 | 0 |

התוצאות נשמרו ב-`02_Data/processed/sprint1_audit.json`.

## 6. נתוני אימון נוספים

נוצרו 40,000 רשומות אימון נוספות באופן דטרמיניסטי בלבד מתוך `Real Train`:

- השיטה: bootstrap עם `random_state=42`.
- הרשומות מקבלות מזהים חדשים בטווח `2,000,000+`.
- לא נעשה שימוש ב-Real Validation, ב-Real Test או בסטטיסטיקות של כלל הנתונים.
- כל הרשומות הנוספות מסומנות במפורש כ-`additional_training_bootstrap_from_real_train`.

מאגר האימון למועמדים הוא לכן:

```text
Training Pool = 6,400 Real Train + 40,000 additional-training rows = 46,400 rows
```

## 7. Preprocessing והגנת Leakage

כל מועמד מאומן באמצעות `sklearn.Pipeline` הכולל:

1. `ColumnTransformer`;
2. `OrdinalEncoder` עבור `AGE`, `DRIVING_EXPERIENCE`, `VEHICLE_YEAR`;
3. `SimpleImputer(strategy="median")` עבור ערכים מספריים;
4. `StandardScaler`;
5. המודל עצמו.

כל רכיב הלומד פרמטרים מותאם בתוך `Pipeline.fit()` לנתוני האימון בלבד. ה-Validation וה-Test מועברים רק דרך `transform`, `predict` או `predict_proba` לאחר האימון.

שמונה תכונות המודל הן:

`AGE`, `DRIVING_EXPERIENCE`, `PAST_ACCIDENTS`, `SPEEDING_VIOLATIONS`, `DUIS`, `ANNUAL_MILEAGE`, `VEHICLE_OWNERSHIP`, `VEHICLE_YEAR`.

## 8. מודלים שהושוו

כל המועמדים אומנו על Training Pool בלבד ונמדדו על Real Validation בלבד:

- Baseline — רוב המחלקה.
- Logistic Regression.
- Random Forest.
- Neural Network A — שכבה נסתרת אחת, 64 נוירונים, ReLU.
- Neural Network B — שתי שכבות נסתרות, 128 ואז 64 נוירונים, ReLU.
- Neural Network C — שתי שכבות נסתרות, 128 ואז 64 נוירונים, `tanh` ורגולריזציה L2.

רשתות הנוירונים הופעלו בתצורה דטרמיניסטית וקצרת-איטרציות בספרינט זה; המטרה הייתה השוואת משפחות המודל במסגרת המתודולוגיה החדשה ולא חיפוש hyperparameters חדש.

## 9. תוצאות Validation ובחירת המודל

| מודל | Accuracy | Precision | Recall | F1 | ROC-AUC | זמן אימון (שנ׳) |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.8143 | 0.6796 | 0.7705 | 0.7222 | **0.8876** | 0.275 |
| Neural Network C | 0.8180 | 0.6855 | 0.7745 | 0.7273 | 0.8874 | 17.572 |
| Neural Network B | 0.8074 | 0.6771 | 0.7365 | 0.7055 | 0.8805 | 10.514 |
| Neural Network A | 0.8124 | 0.7152 | 0.6667 | 0.6901 | 0.8757 | 1.175 |
| Random Forest | 0.7905 | 0.6554 | 0.6986 | 0.6763 | 0.8317 | 1.704 |
| Baseline | 0.6867 | 0.0000 | 0.0000 | 0.0000 | 0.5000 | 0.297 |

**המודל שנבחר: Logistic Regression.**

כלל הבחירה הוא ROC-AUC גבוה ביותר על Real Validation, עם F1 כ-breaker במקרה של תיקו. Logistic Regression השיג ROC-AUC של 0.8876 — הגבוה ביותר. בנוסף, הוא בעל זמן חיזוי נמוך, פרשנות ישירה באמצעות מקדמים ותאימות מלאה למנגנון ההסבר הקיים במערכת.

בשלב זה לא ניגשו ל-Real Test לצורך שינוי ארכיטקטורה, hyperparameters, תכונות או סף החלטה.

## 10. Refit והערכה סופית בלתי תלויה

אחרי הקפאת בחירת Logistic Regression בוצע refit סופי על:

```text
Real Train + Real Validation + additional data שנוצר מ-Real Train בלבד
```

Real Test לא הוכנס ל-refit ולא היה מקור לשום שלב הכנה. לאחר מכן בוצעה הערכה אחת על 2,001 שורות Real Test.

### FINAL TEST RESULTS

| מדד | ערך |
|---|---:|
| Accuracy | 0.8251 |
| Precision | 0.7034 |
| Recall | 0.7640 |
| F1 Score | 0.7324 |
| ROC-AUC | 0.8903 |

מטריצת הבלבול:

```text
[[1172, 202],
 [ 148, 479]]
```

המספרים נשמרים בנפרד ב-`final_test_results`; הם אינם מעורבבים עם תוצאות Validation.

## 11. Artifact, Metadata ותאימות מערכת

ה-artifact הפעיל נבנה מחדש מה-pipeline המתוקן:

- מודל פעיל: `03_Model/model_v2.pkl`.
- Metadata פעיל: `03_Model/model_v2_metadata.json`.
- העתק זהה ל-notebook: `01_Notebook/exported_artifacts/model_v2_sprint1.pkl`.
- SHA-256: `71d1474c36c4719a950e62659c34d28701c6ec66e072e01b18d6f67344932daf`.

אומת שהקובץ הפעיל והעתק ה-notebook זהים ברמת bytes, ושה-hash תואם ל-metadata. ה-metadata מכיל את ספירות המחיצות, טבלת ה-validation, תוצאות ה-test הסופיות, audit ה-leakage ושיטת יצירת הנתונים הנוספים.

בוצעו התאמות תאימות ב-Gradio וב-backend לקריאת שמות שלבי ה-pipeline החדשים: `preprocessor`, `scaler`, `model`.

## 12. Notebook ותיעוד

ה-notebook הראשי עודכן לסדר עבודה מדעי:

1. הגדרות ומקור נתונים;
2. הרצת ה-pipeline הדטרמיניסטי;
3. Data Leakage Validation;
4. השוואת מועמדים על Validation;
5. בחירת מודל;
6. Refit ותוצאות Test סופיות;
7. אימות hash ותאימות artifact.

ה-notebook הורץ מקצה לקצה מ-kernel נקי: 6 תאי קוד, 0 שגיאות. ה-README עודכן כדי לתאר את המתודולוגיה החדשה.

## 13. בדיקות שבוצעו

| בדיקה | תוצאה |
|---|---|
| הרצת pipeline מלאה | עברה |
| בדיקות ID/fingerprint leakage | עברו — כל החפיפות 0 |
| הרצת notebook נקייה | עברה — 0 שגיאות |
| בדיקות backend / model / feature builder | **88 passed** |
| טעינת Gradio עם artifact חדש | עברה |
| SHA-256 והעתק artifact | עברו |

אזהרות בלבד: הופיעה אזהרת convergence עבור רשתות ה-MLP עקב מגבלת האיטרציות המכוונת; זו אינה שגיאה ואינה משפיעה על בחירת המודל המנצח.

## 14. קבצים מרכזיים שנוספו או עודכנו

- `02_Data/generation/build_training_data.py`
- `02_Data/processed/real_train_sprint1.csv`
- `02_Data/processed/real_validation_sprint1.csv`
- `02_Data/processed/real_test_sprint1.csv`
- `02_Data/processed/additional_training_sprint1.csv`
- `02_Data/processed/training_pool_sprint1.csv`
- `02_Data/processed/sprint1_audit.json`
- `01_Notebook/AutoGuard_AI_V2_ML_Pipeline.ipynb`
- `03_Model/model_v2.pkl`
- `03_Model/model_v2_metadata.json`
- `01_Notebook/exported_artifacts/model_v2_sprint1.pkl`
- `01_Notebook/exported_artifacts/model_v2_sprint1_metadata.json`
- `04_Gradio/gradio_app_v2.py`
- `07_Production_System/backend/predictor_v2.py`
- `07_Production_System/tests/test_quick_predict.py`
- `README.md`

## 15. מה נדחה במכוון

הנושאים הבאים אינם חלק מ-Sprint 1 ולא בוצעו:

- Calibration ועקומות calibration;
- אופטימיזציית threshold או עלות עסקית;
- confidence intervals, bootstrap, DeLong או מבחני מובהקות;
- חיפוש hyperparameters חדש;
- שינוי מודל כלכלי/ROI;
- שינוי UI או פיתוח אלגוריתמים חדשים.

## 16. מסקנת אימות סופית

**האם Test השפיע על אימון או בחירת מודל?** לא.  
**האם תוצאות ה-Test ניתנות לשחזור מקוד וממקור הנתונים?** כן.  
**האם notebook, metadata, artifact, backend ו-Gradio משתמשים באותו artifact פעיל?** כן.

הפרויקט עומד במטרת Sprint 1: הערכת ML עם הפרדה ברורה בין אימון, Validation ובדיקת Test סופית בלתי תלויה.
