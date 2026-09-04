import re


CATEGORIES = {
    "System Design": [
        "system design",
        "architecture",
        "scalability",
        "distributed systems",
        "microservices",
        "system architecture",
    ],
    "Backend Development": [
        "backend",
        "rest api",
        "fastapi",
        "django",
        "flask",
        "backend services",
        "server-side",
    ],
    "Data & SQL": [
        "sql",
        "mysql",
        "postgresql",
        "database",
        "data analysis",
        "pandas",
    ],
    "Cloud & DevOps": [
        "aws",
        "azure",
        "gcp",
        "docker",
        "kubernetes",
        "ci/cd",
        "devops",
        "cloud",
        "deployment",
    ],
    "Programming": [
        "python",
        "java",
        "c++",
        "javascript",
        "typescript",
        "programming",
        "object-oriented programming",
    ],
    "Security": [
        "cybersecurity",
        "security",
        "authentication",
        "authorization",
        "application security",
        "network security",
    ],
    "Frontend Development": [
        "react",
        "frontend",
        "html",
        "css",
        "javascript",
        "user interface",
    ],
    "Testing & Engineering": [
        "testing",
        "unit testing",
        "pytest",
        "debugging",
        "code review",
        "ci/cd",
    ],
}


def clean_text(value):
    """Normalize document text for reliable comparison."""
    value = value or ""
    value = value.lower()

    value = value.replace("•", " ")
    value = value.replace("–", "-")
    value = value.replace("—", "-")

    value = re.sub(r"\s+", " ", value)

    return value.strip()


def contains_term(text, term):
    """
    Match a requirement without accidentally matching
    tiny words inside unrelated words.
    """
    term = clean_text(term)

    if not term:
        return False

    # Multi-word terms can safely use substring matching.
    if " " in term or "/" in term or "-" in term:
        return term in text

    # Word boundary matching for short/single keywords.
    return re.search(
        rf"\b{re.escape(term)}\b",
        text,
    ) is not None


def get_category_results(resume_text, jd_text):
    """Compare resume evidence against JD requirements."""

    results = {}

    for category, keywords in CATEGORIES.items():

        required = [
            keyword
            for keyword in keywords
            if contains_term(jd_text, keyword)
        ]

        if not required:
            continue

        matched = [
            keyword
            for keyword in required
            if contains_term(resume_text, keyword)
        ]

        missing = [
            keyword
            for keyword in required
            if not contains_term(resume_text, keyword)
        ]

        score = round(
            (len(matched) / len(required)) * 100
        )

        results[category] = {
            "score": score,
            "required": required,
            "matched": matched,
            "missing": missing,
        }

    return results


def choose_signal(category_results):
    """Choose the strongest meaningful evidence category."""

    if not category_results:
        return None

    # Prefer categories with actual matched evidence.
    categories_with_matches = {
        category: data
        for category, data in category_results.items()
        if data["matched"]
    }

    if categories_with_matches:
        return max(
            categories_with_matches,
            key=lambda category: (
                categories_with_matches[category]["score"],
                len(categories_with_matches[category]["matched"]),
            ),
        )

    return max(
        category_results,
        key=lambda category: category_results[category]["score"],
    )


def build_reason(signal, selected):
    matched = selected["matched"]
    missing = selected["missing"]

    if matched and missing:
        return (
            f"The resume provides evidence of {signal.lower()} "
            f"through {', '.join(matched[:4])}, while the job "
            f"description also asks for {', '.join(missing[:3])} "
            "that is not clearly demonstrated."
        )

    if matched:
        return (
            f"The resume provides direct evidence of "
            f"{signal.lower()} through "
            f"{', '.join(matched[:5])}. "
            "This aligns with requirements identified in the "
            "job description."
        )

    return (
        f"The job description emphasizes {signal.lower()}, "
        "but the resume does not provide clear matching evidence."
    )


def build_suggestions(signal, selected, rejection_text):
    matched = selected["matched"]
    missing = selected["missing"]

    suggestions = []

    if missing:
        suggestions.append(
            f"Strengthen evidence for {', '.join(missing[:3])} "
            "through relevant projects, coursework, or experience."
        )

        suggestions.append(
            "Use concrete evidence instead of only listing a skill."
        )

    if matched:
        suggestions.append(
            f"Add measurable outcomes to your "
            f"{signal.lower()} experience where genuine."
        )

    if rejection_text:
        suggestions.append(
            "Use the rejection feedback to make recurring gaps "
            "more explicit in future applications."
        )

    suggestions.append(
        "Keep the strongest role-relevant evidence near the "
        "top of the resume."
    )

    return suggestions


def analyze_application(resume, jd, rejection=""):
    """
    Main REFRACT analysis function.

    Returns a structured result that the UI can consume.
    """

    resume_text = clean_text(resume)
    jd_text = clean_text(jd)
    rejection_text = clean_text(rejection)

    category_results = get_category_results(
        resume_text,
        jd_text,
    )

    # ---------------------------------------------
    # No recognizable JD requirements
    # ---------------------------------------------

    if not category_results:
        return {
            "signal": "Role Alignment",
            "confidence": 50,
            "overall_score": 50,
            "reason": (
                "The job description did not contain enough "
                "recognized requirements for a reliable "
                "category-level analysis."
            ),
            "matched": [],
            "missing": [],
            "suggestions": [
                "Add clearer role-specific requirements.",
                "Show concrete project evidence.",
                "Use measurable outcomes where possible.",
            ],
            "breakdown": {},
            "categories": {},
        }

    # ---------------------------------------------
    # Select signal
    # ---------------------------------------------

    signal = choose_signal(category_results)
    selected = category_results[signal]

    # ---------------------------------------------
    # Overall alignment
    # ---------------------------------------------

    scores = [
        data["score"]
        for data in category_results.values()
    ]

    overall_score = round(
        sum(scores) / len(scores)
    )

    # Confidence is based on evidence coverage.
    evidence_count = len(selected["matched"])
    requirement_count = len(selected["required"])

    confidence = selected["score"]

    if evidence_count == 0:
        confidence = 25
    elif evidence_count == 1:
        confidence = min(confidence, 55)

    confidence = max(
        20,
        min(95, confidence),
    )

    # ---------------------------------------------
    # Breakdown
    # ---------------------------------------------

    breakdown = {
        category: data["score"]
        for category, data in category_results.items()
    }

    # ---------------------------------------------
    # Suggestions
    # ---------------------------------------------

    suggestions = build_suggestions(
        signal,
        selected,
        rejection_text,
    )

    return {
        "signal": signal,
        "confidence": confidence,
        "overall_score": overall_score,
        "reason": build_reason(
            signal,
            selected,
        ),
        "matched": selected["matched"],
        "missing": selected["missing"],
        "suggestions": suggestions,
        "breakdown": breakdown,
        "categories": category_results,
    }