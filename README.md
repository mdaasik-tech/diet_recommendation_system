# AI-Based Diet Recommendation System

An educational Streamlit app: profile form -> BMI, BMR, maintenance calories -> goal-based
calorie and protein ranges -> Indian home-food meal plan -> workout split -> PDF report.

**Honest design:** BMI, BMR and calories are plain formulas. Meals are matched by rules from a
CSV adapted from the supplied diet chart. No machine learning is claimed (see `models/README.md`).

## Run it
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
streamlit run app.py
```

## Test it
```bash
pytest
```

## Structure
```
app.py                    Streamlit UI (7 tabs)
modules/calculations.py   BMI, BMR, TDEE, goal targets, macros
modules/safety.py         Adult-only safety gate + disclaimer
modules/diet_engine.py    Loads CSV, matches goal + food preference
modules/workout_engine.py Rule-based workout split
modules/pdf_report.py     ReportLab PDF (wrapped tables, page numbers)
modules/ui.py             Theme CSS and HTML builders (hero, range track, meal timeline)
dataset/diet_meals.csv    32 meal rows from the chart (goal x veg/non-veg x meal time)
tests/                    65 tests
```

## Safety rules built in
- Plans are never generated for under-18s, pregnancy/breastfeeding, diabetes, kidney/liver/heart
  disease, thyroid problems, food allergies or eating-disorder history.
- Every safety question is required; "Prefer not to say" or unanswered also blocks the plan.
- Recomposition is not offered, because the source chart has no such plan.
- Nothing is stored; details live only in the browser session.

## Data note
`source_kcal` values are the chart's approximate numbers. The 6:30 am drink is stored as 5 kcal
(midpoint of the stated 0-10), so the fat-loss rows sum to 1,675 vs the chart's "about 1,700".

Author: Mohammed Aasik.a - https://github.com/mdaasik-tech
