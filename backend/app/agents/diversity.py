from typing import Dict, Any, List


# Some medical conditions where one gender is usually less represented
GENDER_UNDERREP_CONDITIONS = {
    "Type 2 Diabetes": "female",
    "Type 2 Diabetes Mellitus": "female",
    "Heart Disease": "female",
    "Coronary Artery Disease": "female",
    "Cardiovascular Disease": "female",
    "COPD": "female",
    "Chronic Obstructive Pulmonary Disease": "female",
    "Depression": "male",
    "Major Depressive Disorder": "male",
    "Anxiety": "male",
    "Eating Disorders": "male",
    "Osteoporosis": "male",
    "Lung Cancer": "female",
}


def calculate_diversity_score(patient: Dict, trial: Dict, base_score: float) -> Dict[str, Any]:
    diversity_points = 0
    reasons = []

    #Geographic diversity
    trial_locations = trial.get("locations", [])

    if isinstance(trial_locations, str):
        trial_locations = [trial_locations]

    location_text = ""
    for l in trial_locations:
        location_text += str(l).lower() + " "

    if "india" in location_text:
        patient_tier = patient.get("location_tier", "Tier 1")

        if patient_tier == "Tier 2" or patient_tier == "Tier 3":
            diversity_points += 20
            reasons.append({
                "text": "Trial includes India and benefits from participants from smaller cities",
                "weight": "HIGH"
            })
        else:
            diversity_points += 5
            reasons.append({
                "text": "Trial is recruiting in India",
                "weight": "LOW"
            })

    #Gender diversity
    patient_gender = patient.get("gender", "").lower()
    patient_conditions = patient.get("conditions", [])

    for cond in patient_conditions:
        cond_lower = cond.lower() if isinstance(cond, str) else ""

        for known_cond in GENDER_UNDERREP_CONDITIONS:
            needed_gender = GENDER_UNDERREP_CONDITIONS[known_cond]

            if known_cond.lower() in cond_lower:
                if patient_gender == needed_gender:
                    diversity_points += 15
                    reasons.append({
                        "text": f"{cond} studies usually need more {needed_gender} participants",
                        "weight": "HIGH"
                    })
                break

    #Age diversity
    age = patient.get("age")

    if age is not None:
        if age >= 65:
            diversity_points += 10
            reasons.append({
                "text": "Older adults (65+) are often underrepresented in trials",
                "weight": "MEDIUM"
            })
        elif age <= 25:
            diversity_points += 10
            reasons.append({
                "text": "Young adults are needed for balanced age representation",
                "weight": "MEDIUM"
            })

    #Socioeconomic diversity
    income = patient.get("income_bracket")

    if income == "Low":
        diversity_points += 10
        reasons.append({
            "text": "Low-income participants help improve trial accessibility",
            "weight": "MEDIUM"
        })

    final_score = base_score + diversity_points

    if diversity_points >= 20:
        level = "HIGH"
        label = "High Priority Match"
    elif diversity_points >= 10:
        level = "MEDIUM"
        label = "Priority Match"
    else:
        level = "STANDARD"
        label = "Standard Match"

    return {
        "base_score": base_score,
        "diversity_boost": diversity_points,
        "final_score": final_score,
        "diversity_reasons": reasons,
        "priority_level": level,
        "priority_label": label
    }


def optimize_trial_ranking(patient: Dict, eligible_trials: List[Dict]) -> Dict[str, List[Dict]]:
    scored = []

    for item in eligible_trials:
        trial = item.get("trial", item)
        eligibility = item.get("eligibility", {})

        confidence = eligibility.get("confidence", 0.5)
        base_score = confidence * 100

        diversity_data = calculate_diversity_score(patient, trial, base_score)

        item["diversity"] = diversity_data
        scored.append(item)

    # Sort trials based on final score
    scored.sort(
        key=lambda x: x.get("diversity", {}).get("final_score", 0),
        reverse=True
    )

    high = []
    medium = []
    standard = []

    for t in scored:
        level = t.get("diversity", {}).get("priority_level")
        if level == "HIGH":
            high.append(t)
        elif level == "MEDIUM":
            medium.append(t)
        else:
            standard.append(t)

    return {
        "high_priority": high,
        "medium_priority": medium,
        "standard": standard,
        "total_high_priority": len(high),
        "total_medium_priority": len(medium),
        "total_standard": len(standard)
    }


def get_diversity_summary(patient: Dict) -> Dict[str, Any]:
    summary = []

    tier = patient.get("location_tier")
    if tier in ["Tier 2", "Tier 3"]:
        summary.append({
            "factor": "Geographic",
            "description": f"Patient from {tier} city"
        })

    gender = patient.get("gender", "").lower()
    conditions = patient.get("conditions", [])

    for cond in conditions:
        for known_cond in GENDER_UNDERREP_CONDITIONS:
            if known_cond.lower() in cond.lower():
                if gender == GENDER_UNDERREP_CONDITIONS[known_cond]:
                    summary.append({
                        "factor": "Gender Balance",
                        "description": f"{gender} patient for {cond}"
                    })

    age = patient.get("age")
    if age is not None:
        if age >= 65 or age <= 25:
            summary.append({
                "factor": "Age Diversity",
                "description": "Age group often underrepresented in trials"
            })

    if patient.get("income_bracket") == "Low":
        summary.append({
            "factor": "Socioeconomic",
            "description": "Low income background"
        })

    return {
        "diversity_factors": summary,
        "total_factors": len(summary),
        "is_priority_candidate": len(summary) >= 2
    }
