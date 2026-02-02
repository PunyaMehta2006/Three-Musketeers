def generate_explanation(trial, eligibility, diversity):
    explanation = {}

    status = eligibility.get("status", "POSSIBLY_ELIGIBLE")
    confidence = eligibility.get("confidence", 0.5)

    # Status message
    if status == "ELIGIBLE":
        summary = "You qualify for this clinical trial."
        status_label = "You Qualify"
    elif status == "POSSIBLY_ELIGIBLE":
        summary = "You might qualify for this trial, but more details are needed."
        status_label = "Possibly Eligible"
    else:
        summary = "Based on the given information, you may not qualify."
        status_label = "Not Eligible"

    # Why user qualifies
    why_qualify = []
    inclusion = eligibility.get("inclusion_criteria", [])

    for item in inclusion:
        if item.get("status") == "PASS":
            text = item.get("criterion") + " matches your value (" + str(item.get("patient_value")) + ")"
            why_qualify.append(text)

    # Missing info and failed criteria
    concerns = []

    missing_data = eligibility.get("missing_data", [])
    for miss in missing_data:
        concerns.append(
            miss.get("field") + ": " + miss.get("reason")
        )

    for item in inclusion:
        if item.get("status") == "FAIL":
            concerns.append(
                item.get("criterion") + ": " + item.get("reasoning")
            )

    # Next steps
    steps = []

    for miss in missing_data:
        if miss.get("impact") in ["CRITICAL", "HIGH"]:
            steps.append("Get test or report for " + miss.get("field"))

    if trial.get("contact_email"):
        steps.append("Contact trial coordinator at " + trial.get("contact_email"))
    else:
        steps.append("Check ClinicalTrials.gov for contact details")

    if status == "ELIGIBLE":
        steps.append("Talk to your doctor before joining")
    elif status == "POSSIBLY_ELIGIBLE":
        steps.append("Complete missing medical tests")
    else:
        steps.append("Ask your doctor about other trials")

    # Trial details (simple)
    trial_details = {
        "phase": trial.get("phase", "Not mentioned"),
        "sponsor": trial.get("sponsor", "Not mentioned"),
        "location": trial.get("locations", []),
        "intervention": trial.get("interventions", "Not specified")
    }

    # Confidence label
    if confidence > 0.8:
        confidence_label = "High"
    elif confidence > 0.6:
        confidence_label = "Medium"
    else:
        confidence_label = "Low"

    # Final structure
    explanation["trial_id"] = trial.get("nct_id", "")
    explanation["trial_title"] = trial.get("title", "")
    explanation["status"] = status
    explanation["status_label"] = status_label
    explanation["confidence"] = confidence
    explanation["confidence_label"] = confidence_label
    explanation["summary"] = summary
    explanation["why_you_qualify"] = why_qualify
    explanation["concerns"] = concerns
    explanation["next_steps"] = steps
    explanation["trial_details"] = trial_details
    explanation["diversity_priority"] = diversity.get("priority_label", "Standard")

    return explanation


if __name__ == "__main__":

    trial = {
        "nct_id": "NCT123456",
        "title": "MacBook Health Study",
        "phase": "Phase 2",
        "sponsor": "Health Research Org",
        "locations": ["Mumbai", "Delhi"],
        "interventions": "Oral medication",
        "contact_email": "trial@health.org"
    }

    eligibility = {
        "status": "POSSIBLY_ELIGIBLE",
        "confidence": 0.7,
        "inclusion_criteria": [
            {
                "criterion": "Age between 18 and 65",
                "status": "PASS"
            },
            {
                "criterion": "No heart disease",
                "status": "FAIL",
                "reasoning": "Patient reported past heart condition"
            }
        ],
        "missing_data": [
            {
                "field": "blood_test",
                "reason": "Recent blood test not available",
                "impact": "HIGH"
            }
        ]
    }

    diversity = {
        "priority_label": "High Diversity Priority"
    }

    result = generate_explanation(trial, eligibility, diversity)

    print(result)
