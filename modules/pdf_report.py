"""Personalised PDF report built in memory with ReportLab."""
from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .diet_engine import SOURCE_NOTE, format_time
from .safety import DISCLAIMER

NAVY = colors.HexColor("#16273F")
GREEN = colors.HexColor("#1E9E75")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=base["Title"], textColor=NAVY, fontSize=20, spaceAfter=4),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], textColor=GREEN, spaceBefore=12, spaceAfter=6),
        "body": ParagraphStyle("b", parent=base["BodyText"], fontSize=10, leading=14),
        "small": ParagraphStyle("s", parent=base["BodyText"], fontSize=8.5, leading=11, textColor=colors.HexColor("#444444")),
        "cell": ParagraphStyle("c", parent=base["BodyText"], fontSize=9, leading=12),
        "head": ParagraphStyle("h", parent=base["BodyText"], fontSize=9, leading=12, textColor=colors.white, fontName="Helvetica-Bold"),
    }


def _p(text, style):
    return Paragraph(escape(str(text)), style)


def _table(rows, col_widths, styles, header=True):
    data = []
    for r_index, row in enumerate(rows):
        style = styles["head"] if header and r_index == 0 else styles["cell"]
        data.append([_p(cell, style) for cell in row])
    table = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    table.setStyle(TableStyle(commands))
    return table


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(20 * mm, 10 * mm, "Educational tool - not medical advice")
    canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_report(user, metrics, meals, workout):
    """Return PDF bytes.

    user: dict(name, age, sex, height_cm, weight_kg, activity, goal, food_preference,
               experience, workout_days)
    metrics: dict(bmi, bmi_category, bmr, tdee, calorie_range, protein_range,
                  macros (optional), plan_note (optional))
    meals: DataFrame with meal_time, meal_name, food_description, source_kcal
    workout: dict from workout_engine.recommend_workout
    """
    s = _styles()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm, title="Personalised Diet & Fitness Report",
    )
    width = A4[0] - 40 * mm
    story = []

    # 1. Title and date
    story.append(_p("Personalised Diet & Fitness Report", s["title"]))
    story.append(_p(f"Report date: {date.today().strftime('%d %B %Y')}", s["small"]))

    # 2. Profile
    story.append(_p("Your profile", s["h2"]))
    profile_rows = [
        ["Name", user["name"]],
        ["Age / sex (BMR equation)", f"{user['age']} / {user['sex']}"],
        ["Height / weight", f"{user['height_cm']} cm / {user['weight_kg']} kg"],
        ["Activity level", user["activity"]],
        ["Goal", user["goal"]],
        ["Food preference", user["food_preference"]],
        ["Workout experience / days", f"{user['experience']} / {user['workout_days']} days a week"],
    ]
    story.append(_table(profile_rows, [width * 0.4, width * 0.6], s, header=False))

    # 3-8. Estimates
    story.append(_p("Your estimates", s["h2"]))
    cal_low, cal_high = metrics["calorie_range"]
    pro_low, pro_high = metrics["protein_range"]
    est_rows = [
        ["Measure", "Value"],
        ["BMI", f"{metrics['bmi']} ({metrics['bmi_category']})"],
        ["BMR (Mifflin-St Jeor)", f"{metrics['bmr']} kcal/day"],
        ["Estimated maintenance (TDEE)", f"{metrics['tdee']} kcal/day"],
        ["Goal calorie range", f"{cal_low}-{cal_high} kcal/day"],
        ["Protein range", f"{pro_low}-{pro_high} g/day"],
    ]
    macros = metrics.get("macros")
    if macros:
        est_rows.append([
            "Macro estimate (illustrative midpoint)",
            f"Protein {macros['protein_g']} g, Carbs {macros['carbs_g']} g, Fat {macros['fat_g']} g",
        ])
    story.append(_table(est_rows, [width * 0.45, width * 0.55], s))
    story.append(Spacer(1, 4))
    story.append(_p(
        "BMI is a screening measure and cannot tell muscle from fat. All values are "
        "estimates, not laboratory measurements.", s["small"]))

    # 9. Meal plan
    story.append(_p(f"Sample meal plan ({user['food_preference']})", s["h2"]))
    if len(meals):
        meal_rows = [["Time", "Meal", "What to eat", "Approx. kcal"]]
        for _, m in meals.iterrows():
            meal_rows.append([
                format_time(m["meal_time"]), m["meal_name"],
                m["food_description"], f"~{int(m['source_kcal'])}",
            ])
        story.append(_table(meal_rows, [width * 0.14, width * 0.17, width * 0.55, width * 0.14], s))
        story.append(Spacer(1, 4))
        story.append(_p(f"Sample day total: about {int(meals['source_kcal'].sum())} kcal.", s["body"]))
    else:
        story.append(_p("No matching meal plan was available.", s["body"]))
    if metrics.get("plan_note"):
        story.append(_p(metrics["plan_note"], s["small"]))

    # 10. Workout
    story.append(_p("Workout suggestion", s["h2"]))
    story.append(_p(f"{workout['split']} - {workout['sessions_per_week']} sessions per week", s["body"]))
    story.append(_p(workout["summary"], s["small"]))
    story.append(Spacer(1, 4))
    story.append(_table([["Weekly schedule"]] + [[d] for d in workout["schedule"]], [width], s))
    story.append(Spacer(1, 4))
    for note in workout["notes"]:
        story.append(_p(f"- {note}", s["small"]))

    # 11-12. Disclaimer and source
    story.append(_p("Important notice", s["h2"]))
    story.append(_p(DISCLAIMER, s["small"]))
    story.append(Spacer(1, 4))
    story.append(_p(SOURCE_NOTE, s["small"]))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
