import pytest

from modules import calculations as c


def test_bmi_known_value():
    assert c.calculate_bmi(70, 175) == 22.9


@pytest.mark.parametrize("bmi,cat", [(18.4, "Underweight"), (18.5, "Normal"), (24.9, "Normal"),
                                     (25, "Overweight"), (29.9, "Overweight"), (30, "Obese")])
def test_bmi_categories(bmi, cat):
    assert c.bmi_category(bmi) == cat


def test_bmr_male_and_female():
    assert c.calculate_bmr(70, 175, 25, "Male") == 1674      # 1673.75
    assert c.calculate_bmr(60, 165, 30, "Female") == 1320    # 1320.25


def test_bmr_rejects_bad_sex():
    with pytest.raises(ValueError):
        c.calculate_bmr(70, 175, 25, "Other")


@pytest.mark.parametrize("level,factor", list(c.ACTIVITY_FACTORS.items()))
def test_all_activity_factors(level, factor):
    assert c.calculate_tdee(2000, level) == round(2000 * factor)


def test_unknown_activity_level():
    with pytest.raises(ValueError):
        c.calculate_tdee(2000, "Extreme")


@pytest.mark.parametrize("goal,cal,pro", [
    ("Fat loss", (1500, 1700), (104, 143)),
    ("Muscle gain", (2200, 2300), (104, 143)),
    ("General weight gain", (2400, 2500), (91, 130)),
])
def test_goal_ranges(goal, cal, pro):
    assert c.calculate_goal_targets(2000, 65, goal) == (cal, pro)


def test_recomposition_not_silently_supported():
    with pytest.raises(ValueError):
        c.calculate_goal_targets(2000, 65, "Recomposition")


@pytest.mark.parametrize("h,w", [(0, 65), (170, 0), (-1, 65)])
def test_invalid_height_weight(h, w):
    with pytest.raises(ValueError):
        c.calculate_bmi(w, h)


def test_validate_inputs():
    c.validate_inputs(25, 170, 65)
    with pytest.raises(ValueError):
        c.validate_inputs(17, 170, 65)
    with pytest.raises(ValueError):
        c.validate_inputs(25, 0, 65)


def test_macros():
    m = c.calculate_macros(2000, 130, fat_percent=25)
    assert m == {"protein_g": 130, "fat_g": 56, "carbs_g": 245}
    with pytest.raises(ValueError):
        c.calculate_macros(1000, 240, fat_percent=25)
    with pytest.raises(ValueError):
        c.calculate_macros(2000, 100, fat_percent=40)


def test_low_calorie_warning():
    assert c.low_calorie_warning((1100, 1300), "Female")
    assert c.low_calorie_warning((1600, 1800), "Male") is None
