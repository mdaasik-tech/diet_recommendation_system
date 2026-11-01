"""Adult-only safety gate. The app must not plan for excluded groups."""
from dataclasses import dataclass, field

from .calculations import AGE_RANGE

SAFETY_MESSAGE = (
    "This educational tool cannot safely personalise a plan for this situation. "
    "Please consult a doctor or registered dietitian."
)

DISCLAIMER = (
    "This is an educational tool giving general guidance for healthy adults. "
    "Calorie and protein values are approximate starting estimates, not guaranteed "
    "outcomes or medical prescriptions. It does not replace advice from a doctor "
    "or registered dietitian."
)

SCREENING_QUESTIONS = {
    "pregnant_breastfeeding": "Are you pregnant or breastfeeding?",
    "diabetes": "Do you have diabetes?",
    "organ_disease": "Do you have kidney, liver or heart disease?",
    "thyroid": "Do you have a thyroid problem?",
    "food_allergy": "Do you have any food allergies?",
    "eating_disorder": "Do you have a history of an eating disorder?",
}

PLACEHOLDER = "Select an answer"
ANSWER_OPTIONS = [PLACEHOLDER, "No", "Yes", "Prefer not to say"]


@dataclass
class SafetyResult:
    eligible: bool
    reasons: list = field(default_factory=list)


def evaluate_eligibility(age, answers):
    """Eligible only if age is in range and EVERY question is explicitly 'No'."""
    reasons = []

    if age < AGE_RANGE[0]:
        reasons.append("Automated plans are only for adults (18+).")
    elif age > AGE_RANGE[1]:
        reasons.append(f"This prototype supports ages up to {AGE_RANGE[1]}.")

    unanswered = [
        q for key, q in SCREENING_QUESTIONS.items()
        if answers.get(key, PLACEHOLDER) == PLACEHOLDER
    ]
    if unanswered:
        reasons.append("Please answer every safety question.")

    for key, question in SCREENING_QUESTIONS.items():
        answer = answers.get(key, PLACEHOLDER)
        if answer == "Yes":
            reasons.append(f"Answered 'Yes': {question}")
        elif answer == "Prefer not to say":
            reasons.append(f"Eligibility cannot be established: {question}")

    return SafetyResult(eligible=not reasons, reasons=reasons)
