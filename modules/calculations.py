"""Formula-based health calculations. None of this is machine learning."""

ACTIVITY_FACTORS = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Very active": 1.725,
}

ACTIVITY_DESCRIPTIONS = {
    "Sedentary": "Desk work, little or no exercise",
    "Light": "Exercise 1-3 days a week",
    "Moderate": "Exercise 3-5 days a week",
    "Very active": "Hard training 6-7 days a week or physical job",
}

GOAL_SETTINGS = {
    "Fat loss": {
        "calorie_adjustment": (-500, -300),
        "protein_g_per_kg": (1.6, 2.2),
        "weekly_change": "about 0.25-0.75 kg loss",
    },
    "Muscle gain": {
        "calorie_adjustment": (200, 300),
        "protein_g_per_kg": (1.6, 2.2),
        "weekly_change": "about 0.25-0.5 kg gain",
    },
    "General weight gain": {
        "calorie_adjustment": (400, 500),
        "protein_g_per_kg": (1.4, 2.0),
        "weekly_change": "about 0.4-0.5 kg gain",
    },
}

AGE_RANGE = (18, 80)
HEIGHT_RANGE_CM = (100, 230)
WEIGHT_RANGE_KG = (30, 250)


def validate_inputs(age, height_cm, weight_kg):
    """Raise ValueError listing every problem with the numeric inputs."""
    errors = []
    if not AGE_RANGE[0] <= age <= AGE_RANGE[1]:
        errors.append(f"Age must be between {AGE_RANGE[0]} and {AGE_RANGE[1]}.")
    if not HEIGHT_RANGE_CM[0] <= height_cm <= HEIGHT_RANGE_CM[1]:
        errors.append(
            f"Height must be between {HEIGHT_RANGE_CM[0]} and {HEIGHT_RANGE_CM[1]} cm."
        )
    if not WEIGHT_RANGE_KG[0] <= weight_kg <= WEIGHT_RANGE_KG[1]:
        errors.append(
            f"Weight must be between {WEIGHT_RANGE_KG[0]} and {WEIGHT_RANGE_KG[1]} kg."
        )
    if errors:
        raise ValueError(" ".join(errors))


def calculate_bmi(weight_kg, height_cm):
    if weight_kg <= 0 or height_cm <= 0:
        raise ValueError("Height and weight must be positive.")
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_bmr(weight_kg, height_cm, age, sex):
    """Mifflin-St Jeor equation."""
    if sex not in ("Male", "Female"):
        raise ValueError("Sex must be 'Male' or 'Female' (BMR equation choice).")
    value = 10 * weight_kg + 6.25 * height_cm - 5 * age
    value += 5 if sex == "Male" else -161
    return round(value)


def calculate_tdee(bmr, activity_level):
    if activity_level not in ACTIVITY_FACTORS:
        raise ValueError(f"Unknown activity level: {activity_level}")
    return round(bmr * ACTIVITY_FACTORS[activity_level])


def calculate_goal_targets(tdee, weight_kg, goal):
    """Return (calorie_range, protein_range) using the supplied chart's ranges."""
    if goal not in GOAL_SETTINGS:
        raise ValueError(
            f"'{goal}' is not covered by the supplied diet chart. "
            f"Supported goals: {', '.join(GOAL_SETTINGS)}."
        )
    settings = GOAL_SETTINGS[goal]
    low_adj, high_adj = settings["calorie_adjustment"]
    low_protein, high_protein = settings["protein_g_per_kg"]

    calorie_range = (round(tdee + low_adj), round(tdee + high_adj))
    protein_range = (round(weight_kg * low_protein), round(weight_kg * high_protein))
    return calorie_range, protein_range


def midpoint(value_range):
    return round(sum(value_range) / 2)


def calculate_macros(calories, protein_g, fat_percent=25):
    """Estimate macros: protein 4 kcal/g, carbs 4 kcal/g, fat 9 kcal/g."""
    if not 20 <= fat_percent <= 30:
        raise ValueError("Fat should be about 20-30% of calories per the chart.")
    protein_kcal = protein_g * 4
    fat_kcal = calories * (fat_percent / 100)
    if protein_kcal + fat_kcal > calories:
        raise ValueError("Protein and fat targets exceed the calorie budget.")
    carbs_kcal = calories - protein_kcal - fat_kcal
    return {
        "protein_g": round(protein_g),
        "fat_g": round(fat_kcal / 9),
        "carbs_g": round(carbs_kcal / 4),
    }


def low_calorie_warning(calorie_range, sex):
    """General caution when the lower end of the range is very low."""
    floor = 1500 if sex == "Male" else 1200
    if calorie_range[0] < floor:
        return (
            f"The lower end of your range ({calorie_range[0]} kcal) is quite low. "
            "Please speak to a doctor or registered dietitian before eating this little."
        )
    return None


def bmi_goal_note(bmi, goal):
    """Soft caution only; BMI alone never decides the goal."""
    if bmi < 18.5 and goal == "Fat loss":
        return (
            "Your BMI is in the underweight range, so a fat-loss goal may not suit you. "
            "BMI is only a screening number, so please check with a professional."
        )
    if bmi >= 30 and goal in ("Muscle gain", "General weight gain"):
        return (
            "Your BMI is in the obese range. BMI cannot tell muscle from fat, "
            "but a calorie surplus may not be the best fit. Consider professional advice."
        )
    return None
