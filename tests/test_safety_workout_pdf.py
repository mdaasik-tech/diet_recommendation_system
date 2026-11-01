import pytest

from modules import safety, workout_engine as w
from modules.diet_engine import load_diet_data, recommend_meals
from modules.pdf_report import build_report

ALL_NO = {k: "No" for k in safety.SCREENING_QUESTIONS}


def test_eligible_adult_all_no():
    assert safety.evaluate_eligibility(25, ALL_NO).eligible


def test_under_18_blocked():
    assert not safety.evaluate_eligibility(17, ALL_NO).eligible


@pytest.mark.parametrize("key", list(safety.SCREENING_QUESTIONS))
def test_any_yes_blocked(key):
    assert not safety.evaluate_eligibility(25, {**ALL_NO, key: "Yes"}).eligible


def test_prefer_not_to_say_and_unanswered_blocked():
    assert not safety.evaluate_eligibility(25, {**ALL_NO, "diabetes": "Prefer not to say"}).eligible
    assert not safety.evaluate_eligibility(25, {}).eligible


@pytest.mark.parametrize("exp,days,split", [
    ("Beginner", 2, "Full Body"), ("Beginner", 3, "Full Body"), ("Beginner", 4, "Upper / Lower"),
    ("Intermediate", 3, "Full Body"), ("Intermediate", 4, "Upper / Lower"),
    ("Intermediate", 5, "Push / Pull / Legs"), ("Advanced", 6, "Push / Pull / Legs"),
])
def test_workout_rules(exp, days, split):
    assert w.recommend_workout(exp, days)["split"] == split


def test_beginner_many_days_capped():
    assert w.recommend_workout("Beginner", 6)["sessions_per_week"] == 4


def test_bro_split_only_for_experienced():
    assert w.recommend_workout("Advanced", 5, "Bro Split")["split"] == "Bro Split"
    assert w.recommend_workout("Beginner", 5, "Bro Split")["split"] != "Bro Split"


def test_workout_has_recovery_note():
    assert any("Rest" in n for n in w.recommend_workout("Beginner", 3)["notes"])


def test_pdf_builds_and_handles_long_text():
    user = {"name": "Test <User> & Co", "age": 25, "sex": "Male", "height_cm": 175, "weight_kg": 70,
            "activity": "Light", "goal": "Muscle gain", "food_preference": "Non-vegetarian",
            "experience": "Beginner", "workout_days": 3}
    metrics = {"bmi": 22.9, "bmi_category": "Normal", "bmr": 1674, "tdee": 2302,
               "calorie_range": (2502, 2602), "protein_range": (112, 154),
               "macros": {"protein_g": 133, "fat_g": 70, "carbs_g": 330}, "plan_note": "note"}
    meals = recommend_meals(load_diet_data(), "Muscle gain", "Non-vegetarian")
    pdf = build_report(user, metrics, meals, w.recommend_workout("Beginner", 3))
    assert pdf.startswith(b"%PDF") and len(pdf) > 2000
