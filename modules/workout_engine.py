"""Transparent rule-based workout split suggestion."""

SPLIT_OPTIONS = ["Automatic", "PPL", "Bro Split"]

_ROTATIONS = {
    "Full Body": ["Full body"],
    "Upper / Lower": ["Upper body", "Lower body"],
    "Push / Pull / Legs": ["Push (chest, shoulders, triceps)", "Pull (back, biceps)", "Legs and core"],
    "Bro Split": ["Chest", "Back", "Shoulders", "Arms", "Legs", "Weak points + core"],
}

_SUMMARIES = {
    "Full Body": "Every session trains the whole body, which suits beginners and low weekly days.",
    "Upper / Lower": "Alternates upper and lower body sessions, so each area is trained about twice a week.",
    "Push / Pull / Legs": "Splits training into pushing, pulling and legs; needs 5-6 days and good recovery.",
    "Bro Split": "One body part per session. Each muscle may be trained only once a week.",
}

GENERAL_NOTES = [
    "Rest days matter: muscles recover and grow between sessions, so do not skip them.",
    "Add walking on non-training days and aim for 7-9 hours of sleep.",
    "If you have pain, an injury or a medical limitation, get qualified guidance before exercising.",
]


def _build(split, sessions, extra_notes=None):
    rotation = _ROTATIONS[split]
    schedule = [f"Day {i + 1}: {rotation[i % len(rotation)]}" for i in range(sessions)]
    notes = list(extra_notes or []) + GENERAL_NOTES
    return {
        "split": split,
        "summary": _SUMMARIES[split],
        "sessions_per_week": sessions,
        "schedule": schedule,
        "notes": notes,
    }


def recommend_workout(experience, days_per_week, preferred_split="Automatic"):
    """Return a dict describing the suggested split. General example, not a promise."""
    if days_per_week < 2:
        raise ValueError("At least 2 workout days are needed for a split suggestion.")

    note = None
    if preferred_split == "Bro Split":
        if experience == "Beginner":
            note = "Bro Split is meant for experienced users, so a beginner-friendly option was chosen instead."
        else:
            return _build(
                "Bro Split",
                min(days_per_week, 6),
                ["Review weekly volume and recovery; each muscle group may only be trained once weekly."],
            )
    elif preferred_split == "PPL" and days_per_week >= 5:
        return _build("Push / Pull / Legs", days_per_week)

    extra = [note] if note else []

    if experience == "Beginner":
        if days_per_week <= 3:
            return _build("Full Body", days_per_week, extra)
        extra.append("Beginners gain well from about 4 hard sessions; use extra days for walking.")
        return _build("Upper / Lower", 4, extra)

    # Intermediate / Advanced
    if days_per_week <= 3:
        return _build("Full Body", days_per_week, extra)
    if days_per_week == 4:
        return _build("Upper / Lower", 4, extra)
    return _build("Push / Pull / Legs", days_per_week, extra)
