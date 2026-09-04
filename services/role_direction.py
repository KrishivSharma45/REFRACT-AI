def _normalise(value):
    return str(value or "").strip().lower()


def _score_for_category(breakdown, keywords):
    """
    Find the strongest matching category score.
    """

    best_score = 0

    for category, score in breakdown.items():

        category_text = _normalise(category)

        for keyword in keywords:

            if keyword in category_text:

                try:
                    best_score = max(
                        best_score,
                        float(score),
                    )
                except (
                    ValueError,
                    TypeError,
                ):
                    pass

    return best_score


def detect_role_directions(breakdown):
    """
    Estimate role directions from the evidence
    categories produced by REFRACT.

    This is an evidence-based direction signal,
    not a prediction of hiring outcomes.
    """

    if not breakdown:
        return []

    role_profiles = [
        {
            "role": "Software Engineering",
            "keywords": [
                "technical",
                "technical skills",
                "programming",
                "engineering",
                "coding",
            ],
            "description": (
                "Strong alignment with general software "
                "engineering work."
            ),
        },

        {
            "role": "Backend Development",
            "keywords": [
                "backend",
                "technical",
                "programming",
                "engineering",
                "systems",
            ],
            "description": (
                "Your evidence supports backend and "
                "server-side development."
            ),
        },

        {
            "role": "Frontend Development",
            "keywords": [
                "frontend",
                "front end",
                "ui",
                "technical",
                "projects",
            ],
            "description": (
                "Your evidence supports interface-focused "
                "software development."
            ),
        },

        {
            "role": "Data / Analytics",
            "keywords": [
                "data",
                "analytics",
                "analysis",
                "technical",
                "quantitative",
            ],
            "description": (
                "Your evidence shows potential alignment "
                "with data and analytical roles."
            ),
        },

        {
            "role": "Product / Technical Product",
            "keywords": [
                "product",
                "communication",
                "leadership",
                "projects",
                "technical",
            ],
            "description": (
                "Your evidence combines technical and "
                "product-oriented capabilities."
            ),
        },

        {
            "role": "Cybersecurity",
            "keywords": [
                "security",
                "cybersecurity",
                "cyber",
                "technical",
                "systems",
            ],
            "description": (
                "Your evidence supports security-focused "
                "technical roles."
            ),
        },
    ]

    results = []

    for profile in role_profiles:

        score = _score_for_category(
            breakdown,
            profile["keywords"],
        )

        if score <= 0:
            continue

        results.append(
            {
                "role": profile["role"],
                "score": round(score),
                "description": profile["description"],
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:5]


def get_primary_role_direction(breakdown):
    """
    Return the strongest current role direction.
    """

    directions = detect_role_directions(
        breakdown
    )

    if not directions:
        return {
            "role": "Explore",
            "score": 0,
            "description": (
                "Run an analysis with more evidence "
                "to identify a stronger role direction."
            ),
        }

    return directions[0]


def get_role_direction_summary(breakdown):
    """
    Return a concise explanation of the strongest
    role direction.
    """

    primary = get_primary_role_direction(
        breakdown
    )

    if primary["score"] <= 0:
        return primary["description"]

    return (
        f'{primary["role"]} currently has the '
        f'strongest evidence alignment at '
        f'{primary["score"]}%.'
    )