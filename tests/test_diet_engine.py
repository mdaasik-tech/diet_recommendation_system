import pytest

from modules import diet_engine as d

GOALS = ["Fat loss", "Muscle gain", "General weight gain"]


@pytest.fixture(scope="module")
def df():
    return d.load_diet_data()


@pytest.mark.parametrize("goal", GOALS)
@pytest.mark.parametrize("pref", ["Vegetarian", "Non-vegetarian"])
def test_goal_and_preference_matching(df, goal, pref):
    meals = d.recommend_meals(df, goal, pref)
    assert len(meals) > 0
    assert set(meals["goal"]) == {goal}
    assert set(meals["food_preference"]) == {pref}


def test_vegetarian_has_no_meat_or_egg(df):
    text = " ".join(d.recommend_meals(df, "Muscle gain", "Vegetarian")["food_description"]).lower()
    for word in ("chicken", "fish", "egg"):
        assert word not in text


def test_non_veg_contains_animal_protein(df):
    text = " ".join(d.recommend_meals(df, "Fat loss", "Non-vegetarian")["food_description"]).lower()
    assert "chicken" in text and "egg" in text


@pytest.mark.parametrize("goal,total", [("Fat loss", 1675), ("Muscle gain", 2600), ("General weight gain", 3000)])
def test_sample_totals_match_source(df, goal, total):
    assert d.sample_day_total(d.recommend_meals(df, goal, "Vegetarian")) == total


def test_missing_plan_gives_empty_and_message(df):
    meals = d.recommend_meals(df, "Recomposition", "Vegetarian")
    assert meals.empty
    assert "No meal plan" in d.no_plan_message("Recomposition", "Vegetarian")


def test_meals_sorted_by_time(df):
    times = list(d.recommend_meals(df, "Fat loss", "Vegetarian")["meal_time"])
    assert times == sorted(times)


def test_format_time():
    assert d.format_time("06:30") == "6:30 am"
    assert d.format_time("13:30") == "1:30 pm"
    assert d.format_time("12:00") == "12:00 pm"


def test_flag_dislikes(df):
    meals = d.flag_dislikes(d.recommend_meals(df, "Fat loss", "Vegetarian"), "paneer, tofu")
    assert any("paneer" in n for n in meals["note"])


def test_compare_with_target():
    assert "close" in d.compare_with_target(1700, (1500, 1700))
    assert "differs" in d.compare_with_target(3000, (1500, 1700))
