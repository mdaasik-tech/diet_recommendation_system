from modules import ui
from modules.diet_engine import load_diet_data, recommend_meals, flag_dislikes


def test_callout_escapes_html():
    out = ui.callout("<script>alert(1)</script>", title="a & b")
    assert "<script>" not in out and "&lt;script&gt;" in out


def test_timeline_has_every_meal_and_escapes():
    meals = flag_dislikes(recommend_meals(load_diet_data(), "Fat loss", "Vegetarian"), "paneer")
    out = ui.meal_timeline(meals)
    assert out.count('<li class="meal">') == len(meals)
    assert "Contains paneer" in out


def test_target_panel_positions_inside_track():
    out = ui.target_panel("Fat loss", 1410, 1610, 1910, "about 0.25-0.75 kg loss")
    assert "1,410 to 1,610" in out and "Maintenance 1,910" in out


def test_macro_bar_percentages_sum_to_100():
    import re
    out = ui.macro_bar({"protein_g": 130, "carbs_g": 245, "fat_g": 56})
    widths = [float(x) for x in re.findall(r"width:([\d.]+)%", out)]
    assert abs(sum(widths) - 100) < 0.5


def test_schedule_splits_day_and_focus():
    assert "<b>Day 1</b><span>Upper body</span>" in ui.schedule(["Day 1: Upper body"])
