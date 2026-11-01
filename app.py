"""AI-Based Diet Recommendation System - Streamlit app (educational)."""
import streamlit as st

from modules import calculations as calc
from modules import diet_engine, safety, ui, workout_engine
from modules.pdf_report import build_report

st.set_page_config(page_title="Diet and Fitness Planner", page_icon="🥗", layout="wide")
ui.inject_css()

GOALS = list(calc.GOAL_SETTINGS)


@st.cache_data
def get_diet_data():
    return diet_engine.load_diet_data()


def build_plan(profile, answers):
    """Run the safety gate, then all calculations. Returns (plan | None, problems)."""
    try:
        calc.validate_inputs(profile["age"], profile["height_cm"], profile["weight_kg"])
    except ValueError as err:
        return None, [str(err)]
    if not profile["name"].strip():
        return None, ["Enter your name."]

    result = safety.evaluate_eligibility(profile["age"], answers)
    if not result.eligible:
        return None, result.reasons + [safety.SAFETY_MESSAGE]

    bmi = calc.calculate_bmi(profile["weight_kg"], profile["height_cm"])
    bmr = calc.calculate_bmr(profile["weight_kg"], profile["height_cm"], profile["age"], profile["sex"])
    tdee = calc.calculate_tdee(bmr, profile["activity"])
    calorie_range, protein_range = calc.calculate_goal_targets(tdee, profile["weight_kg"], profile["goal"])

    meals = diet_engine.recommend_meals(get_diet_data(), profile["goal"], profile["food_preference"])
    meals = diet_engine.flag_dislikes(meals, profile["dislikes"])
    workout = workout_engine.recommend_workout(
        profile["experience"], profile["workout_days"], profile["preferred_split"]
    )
    return {
        "profile": profile,
        "bmi": bmi,
        "bmi_category": calc.bmi_category(bmi),
        "bmr": bmr,
        "tdee": tdee,
        "calorie_range": calorie_range,
        "protein_range": protein_range,
        "meals": meals,
        "workout": workout,
    }, []


def tab_home():
    ui.show(ui.hero())
    left, right = st.columns(2)
    with left:
        st.subheader("What you get")
        st.markdown(
            "- Your BMI, BMR and maintenance calories\n"
            "- A daily calorie and protein range for your goal\n"
            "- A day of vegetarian or non-vegetarian Indian home meals\n"
            "- A workout split that fits your experience and free days\n"
            "- A PDF report to save or print"
        )
    with right:
        st.subheader("How the numbers are made")
        st.write(
            "BMI, BMR and calories come from standard formulas. Meals come from your diet chart and are "
            "matched by simple rules. There is no machine learning in this version, because there is no "
            "trustworthy dataset to train one."
        )
    ui.show(ui.callout(safety.DISCLAIMER, "note", title="Before you start"))


def tab_profile():
    st.header("Your profile")
    ui.show(ui.callout("Your details stay in this browser session. Nothing is saved or sent anywhere."))
    with st.form("profile_form"):
        st.subheader("About you")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=1, max_value=100, value=22,
                                  help="This version supports adults aged 18 to 80.")
            sex = st.selectbox("Sex for BMR equation", ["Male", "Female"])
        with c2:
            height = st.number_input("Height (cm)", min_value=50.0, max_value=260.0, value=170.0)
            weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=65.0)
            activity = st.selectbox(
                "Activity level", list(calc.ACTIVITY_FACTORS),
                format_func=lambda a: f"{a}: {calc.ACTIVITY_DESCRIPTIONS[a]}",
            )

        st.subheader("Your goal and food")
        c3, c4 = st.columns(2)
        with c3:
            goal = st.selectbox("Fitness goal", GOALS)
        with c4:
            food_preference = st.selectbox("Food preference", ["Vegetarian", "Non-vegetarian"])
        dislikes = st.text_input("Foods you dislike (optional)", placeholder="for example: paneer, soya")

        st.subheader("Training")
        c5, c6, c7 = st.columns(3)
        with c5:
            experience = st.selectbox("Workout experience", ["Beginner", "Intermediate", "Advanced"])
        with c6:
            workout_days = st.selectbox("Workout days a week", [2, 3, 4, 5, 6], index=1)
        with c7:
            preferred_split = st.selectbox("Preferred split (optional)", workout_engine.SPLIT_OPTIONS)

        st.subheader("Safety check")
        st.caption("Answer every question. This tool cannot make a plan if any answer is Yes, "
                   "Prefer not to say, or left blank.")
        answers = {}
        q1, q2 = st.columns(2)
        for i, (key, question) in enumerate(safety.SCREENING_QUESTIONS.items()):
            with (q1 if i % 2 == 0 else q2):
                choice = st.radio(question, safety.ANSWER_OPTIONS[1:], index=None,
                                  horizontal=True, key=f"safety_{key}")
                answers[key] = choice or safety.PLACEHOLDER
        submitted = st.form_submit_button("Create my plan")

    if submitted:
        profile = {
            "name": name, "age": int(age), "sex": sex, "height_cm": height, "weight_kg": weight,
            "activity": activity, "goal": goal, "food_preference": food_preference,
            "experience": experience, "workout_days": workout_days,
            "preferred_split": preferred_split, "dislikes": dislikes,
        }
        plan, problems = build_plan(profile, answers)
        st.session_state["plan"] = plan
        if plan:
            ui.show(ui.callout("Open the Results, Meals, Workout and Report tabs to see it.",
                               title="Your plan is ready"))
        else:
            ui.show(ui.callout("", "warn", title="We could not create a plan yet", items=problems))


def need_plan():
    if not st.session_state.get("plan"):
        ui.show(ui.callout("Fill in the Profile tab and choose Create my plan.", title="Nothing to show yet"))
        return None
    return st.session_state["plan"]


def tab_results():
    plan = need_plan()
    if not plan:
        return
    p = plan["profile"]
    st.header(f"Results for {p['name']}")

    low, high = plan["calorie_range"]
    ui.show(ui.target_panel(p["goal"], low, high, plan["tdee"], calc.GOAL_SETTINGS[p["goal"]]["weekly_change"]))

    plow, phigh = plan["protein_range"]
    ui.show(ui.stat_row([
        ("Protein a day", f"{plow} to {phigh} g", f"{calc.GOAL_SETTINGS[p['goal']]['protein_g_per_kg'][0]} to "
                                                  f"{calc.GOAL_SETTINGS[p['goal']]['protein_g_per_kg'][1]} g per kg"),
        ("BMI", str(plan["bmi"]), ui.bmi_chip(plan["bmi_category"])),
        ("BMR", f"{plan['bmr']:,}", "kcal at complete rest"),
        ("Maintenance", f"{plan['tdee']:,}", "kcal to hold your weight"),
    ]))
    st.caption("BMI is a screening number. It cannot tell muscle from fat.")

    for warning in (calc.low_calorie_warning(plan["calorie_range"], p["sex"]),
                    calc.bmi_goal_note(plan["bmi"], p["goal"])):
        if warning:
            ui.show(ui.callout(warning, "warn"))

    st.subheader("Where your calories come from")
    fat_pct = st.slider("Fat share of calories (%)", 20, 30, 25, key="fat_pct")
    try:
        plan["macros"] = calc.calculate_macros(calc.midpoint(plan["calorie_range"]),
                                               calc.midpoint(plan["protein_range"]), fat_pct)
        ui.show(ui.macro_bar(plan["macros"]))
        st.caption("Estimated from the middle of your calorie and protein ranges. These are not lab measurements.")
    except ValueError as err:
        plan["macros"] = None
        ui.show(ui.callout(str(err), "warn", title="Macros could not be calculated"))


def tab_diet():
    plan = need_plan()
    if not plan:
        return
    p, meals = plan["profile"], plan["meals"]
    st.header(f"A day of meals for {p['goal'].lower()}")
    st.caption(f"{p['food_preference']} option")
    if meals.empty:
        ui.show(ui.callout(diet_engine.no_plan_message(p["goal"], p["food_preference"]), "warn"))
        return

    total = diet_engine.sample_day_total(meals)
    summary = diet_engine.SOURCE_SAMPLE_SUMMARY[p["goal"]]
    note = (
        f"This sample day adds up to about {total:,} kcal. The chart lists about {summary['kcal']:,} kcal "
        f"and {summary['protein']} protein. "
        + diet_engine.compare_with_target(total, plan["calorie_range"])
    )
    ui.show(f'<div class="day-note"><p>{ui._e(note)}</p></div>')
    ui.show(ui.meal_timeline(meals))
    if p["food_preference"] == "Vegetarian" and p["goal"] == "Muscle gain":
        ui.show(ui.callout(diet_engine.VEG_PROTEIN_TIP, "note"))

    with st.expander("Adjust portions for your build"):
        for note in diet_engine.PORTION_NOTES:
            st.write(f"- {note}")
    with st.expander("Swap foods"):
        for category, options in diet_engine.FOOD_SWAPS.items():
            st.write(f"**{category}:** {options}")
        st.caption(diet_engine.BUDGET_PROTEINS)
    with st.expander("Daily habits from the chart"):
        for note in diet_engine.LIFESTYLE_NOTES:
            st.write(f"- {note}")
    st.caption(diet_engine.SOURCE_NOTE)


def tab_workout():
    plan = need_plan()
    if not plan:
        return
    w = plan["workout"]
    st.header(w["split"])
    st.write(w["summary"])
    st.write(f"**{w['sessions_per_week']} training days a week**")
    ui.show(ui.schedule(w["schedule"]))
    ui.show(ui.callout("", "note", title="Recovery and safety", items=w["notes"]))


def tab_report():
    plan = need_plan()
    if not plan:
        return
    p = plan["profile"]
    metrics = {k: plan[k] for k in ("bmi", "bmi_category", "bmr", "tdee", "calorie_range", "protein_range")}
    metrics["macros"] = plan.get("macros")
    metrics["plan_note"] = diet_engine.compare_with_target(
        diet_engine.sample_day_total(plan["meals"]), plan["calorie_range"])
    pdf_bytes = build_report(p, metrics, plan["meals"], plan["workout"])
    st.header("Your report")
    st.write("The PDF holds your estimates, meal plan, workout and the safety notice, ready to save or print.")
    st.download_button("Download my diet report (PDF)", data=pdf_bytes,
                       file_name="personalised_diet_report.pdf", mime="application/pdf")


def tab_about():
    st.header("About this tool")
    st.markdown(
        """
**Methods**
- BMI = weight (kg) divided by height (m) squared
- BMR uses the Mifflin-St Jeor equation (male +5, female -161)
- Maintenance = BMR × activity factor (1.2, 1.375, 1.55 or 1.725)
- Goal ranges come from your chart: fat loss -300 to -500 kcal, muscle gain +200 to +300,
  weight gain +400 to +500; protein 1.6 to 2.2 g per kg (1.4 to 2.0 for weight gain)
- Macros: protein and carbs 4 kcal per gram, fat 9 kcal per gram; fat is about 20 to 30% of calories

**Limits**
- Meal calories are approximate values from the chart, not exact nutrient data.
- The chart has no muscle-recomposition plan, so this tool does not offer one.
- No machine learning is used. It needs a trustworthy, documented dataset (see `models/README.md`).
- Not for under-18s, pregnancy or breastfeeding, diabetes, kidney, liver or heart disease,
  thyroid problems, food allergies, or a history of eating disorders.
        """
    )
    ui.show(ui.callout(safety.DISCLAIMER, "note"))
    st.caption("Project author: Mohammed Aasik.a, github.com/mdaasik-tech")


tabs = st.tabs(["Home", "Profile", "Results", "Meals", "Workout", "Report", "About"])
for tab, render in zip(tabs, [tab_home, tab_profile, tab_results, tab_diet,
                              tab_workout, tab_report, tab_about]):
    with tab:
        render()
