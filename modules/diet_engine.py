"""Rule-based meal matching against meals adapted from the supplied diet chart."""
from pathlib import Path

import pandas as pd

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "dataset" / "diet_meals.csv"

SOURCE_NOTE = "Meal suggestions adapted from the user's supplied Complete Diet Chart PDF."

# Stated in the source for the sample day (not for every user).
SOURCE_SAMPLE_SUMMARY = {
    "Fat loss": {"kcal": 1700, "protein": "100-110 g"},
    "Muscle gain": {"kcal": 2600, "protein": "140-150 g (non-vegetarian sample)"},
    "General weight gain": {"kcal": 3000, "protein": "120-130 g"},
}

FOOD_SWAPS = {
    "Protein": "Eggs, chicken, fish, curd, milk, paneer, dal, chana, rajma, sprouts, "
               "soya chunks, tofu, peanuts, optional whey",
    "Carbohydrates": "Rice, chapati, idli, dosa, millets (ragi, kambu, cholam), oats, poha, "
                     "sweet potato, banana, bread",
    "Healthy fats": "Groundnut, almonds, walnuts, small amount of coconut, measured ghee, "
                    "sesame / groundnut oil, fish",
    "Vegetables and fruits": "Seasonal vegetables, keerai, carrot, beetroot, guava, papaya, "
                             "apple, orange, watermelon",
}

BUDGET_PROTEINS = "Eggs, dal, chana, soya chunks, peanuts, curd and milk are budget-friendly protein options."

PORTION_NOTES = [
    "The sample portions suit an average adult of about 65-75 kg.",
    "Smaller builds or women may reduce rice/chapati and snacks by about 15-20%.",
    "Bigger builds or very active people may increase them by about 15-20%.",
    "These are broad guidelines, not a precise formula; foods do not all scale linearly.",
]

LIFESTYLE_NOTES = [
    "Water: about 2.5-3.5 litres daily.",
    "Sleep: 7-9 hours.",
    "Strength training 3-5 days a week plus walking.",
    "Track your weekly average weight rather than daily changes.",
]

VEG_PROTEIN_TIP = (
    "If your vegetarian protein falls short, add 100 g extra paneer/soya or one scoop of whey."
)


def load_diet_data(path=DEFAULT_DATA_PATH):
    return pd.read_csv(path)


def recommend_meals(diet_df, goal, food_preference):
    """Return only the rows for this goal and food preference (empty if no match)."""
    selected = diet_df[
        (diet_df["goal"] == goal) & (diet_df["food_preference"] == food_preference)
    ]
    return selected.sort_values("meal_time").reset_index(drop=True)


def no_plan_message(goal, food_preference):
    return (
        f"No meal plan is available for '{goal}' ({food_preference}) in the supplied diet chart. "
        "Please choose Fat loss, Muscle gain or General weight gain."
    )


def sample_day_total(meals):
    return int(meals["source_kcal"].sum()) if len(meals) else 0


def compare_with_target(sample_kcal, calorie_range):
    """Honest note on how the sample day relates to the user's own estimate."""
    low, high = calorie_range
    if sample_kcal == 0:
        return ""
    if low * 0.9 <= sample_kcal <= high * 1.1:
        return (
            f"The sample day (about {sample_kcal} kcal) is reasonably close to your estimated "
            f"range ({low}-{high} kcal). Still treat it as an example, not an exact match."
        )
    return (
        f"The sample day (about {sample_kcal} kcal) differs noticeably from your estimated range "
        f"({low}-{high} kcal). Use your own numbers as the target and review portions with a "
        "registered dietitian."
    )


def format_time(hhmm):
    hour, minute = (int(x) for x in str(hhmm).split(":"))
    suffix = "am" if hour < 12 else "pm"
    hour12 = hour % 12 or 12
    return f"{hour12}:{minute:02d} {suffix}"


def flag_dislikes(meals, dislikes_text):
    """Add a 'note' column marking meals that contain a disliked food keyword."""
    meals = meals.copy()
    terms = [t.strip().lower() for t in (dislikes_text or "").split(",") if t.strip()]

    def note(description):
        hits = [t for t in terms if t in description.lower()]
        return f"Contains {', '.join(hits)} - see food swaps" if hits else ""

    meals["note"] = meals["food_description"].apply(note)
    return meals
