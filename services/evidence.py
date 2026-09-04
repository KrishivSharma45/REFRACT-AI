import re


def clean_text(value):
    """Normalize text for evidence comparison."""
    value = value or ""
    value = value.lower()

    value = value.replace("•", " ")
    value = value.replace("–", "-")
    value = value.replace("—", "-")

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def contains_term(text, term):
    """Check whether a term appears as a real word/phrase."""
    text = clean_text(text)
    term = clean_text(term)

    if not term:
        return False

    if " " in term or "/" in term or "-" in term:
        return term in text

    return re.search(
        rf"\b{re.escape(term)}\b",
        text,
    ) is not None


def calculate_evidence_strength(
    keyword,
    resume_text,
    jd_text,
):
    """
    Estimate how strongly the resume demonstrates
    a requirement from the job description.

    This is an evidence signal, not a hiring prediction.
    """

    keyword = clean_text(keyword)
    resume_text = clean_text(resume_text)
    jd_text = clean_text(jd_text)

    if not keyword:
        return {
            "keyword": keyword,
            "score": 0,
            "strength": "Weak",
            "reason": "No requirement was provided.",
        }

    required = contains_term(jd_text, keyword)
    present = contains_term(resume_text, keyword)

    if not required:
        return {
            "keyword": keyword,
            "score": 0,
            "strength": "Weak",
            "reason": "This requirement was not detected in the job description.",
        }

    if not present:
        return {
            "keyword": keyword,
            "score": 0,
            "strength": "Missing",
            "reason": "The resume does not clearly demonstrate this requirement.",
        }

    # Count how often the evidence appears.
    occurrences = len(
        re.findall(
            rf"\b{re.escape(keyword)}\b",
            resume_text,
        )
    )

    # Basic evidence scoring.
    if occurrences >= 3:
        score = 90
        strength = "Strong"
        reason = (
            "The requirement appears repeatedly in the resume, "
            "providing stronger direct evidence."
        )
    elif occurrences == 2:
        score = 75
        strength = "Moderate"
        reason = (
            "The requirement appears more than once, "
            "showing reasonable supporting evidence."
        )
    else:
        score = 55
        strength = "Moderate"
        reason = (
            "The requirement appears in the resume, "
            "but the evidence is limited."
        )

    return {
        "keyword": keyword,
        "score": score,
        "strength": strength,
        "reason": reason,
    }


def analyze_evidence_strength(
    resume_text,
    jd_text,
    matched,
    missing,
):
    """
    Analyze the strength of matched and missing evidence.
    """

    results = []

    matched = matched or []
    missing = missing or []

    for keyword in matched:
        results.append(
            calculate_evidence_strength(
                keyword,
                resume_text,
                jd_text,
            )
        )

    for keyword in missing:
        results.append(
            {
                "keyword": keyword,
                "score": 0,
                "strength": "Missing",
                "reason": (
                    "This requirement appears in the job description "
                    "but is not clearly demonstrated in the resume."
                ),
            }
        )

    strength_order = {
        "Strong": 0,
        "Moderate": 1,
        "Weak": 2,
        "Missing": 3,
    }

    results.sort(
        key=lambda item: (
            strength_order.get(
                item["strength"],
                4,
            ),
            -item["score"],
        )
    )

    return results


def get_evidence_summary(evidence_results):
    """Return a compact summary for the Results page."""

    strong = sum(
        1
        for item in evidence_results
        if item["strength"] == "Strong"
    )

    moderate = sum(
        1
        for item in evidence_results
        if item["strength"] == "Moderate"
    )

    weak = sum(
        1
        for item in evidence_results
        if item["strength"] == "Weak"
    )

    missing = sum(
        1
        for item in evidence_results
        if item["strength"] == "Missing"
    )

    return {
        "strong": strong,
        "moderate": moderate,
        "weak": weak,
        "missing": missing,
        "total": len(evidence_results),
    }