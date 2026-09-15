from collections import Counter


def detect_patterns(history):
    """
    Detect recurring categories, signals and evidence gaps
    across saved REFRACT analyses.

    This identifies patterns in the user's analysis history.
    It does not claim to know the actual recruiter's decision.
    """

    if not history:
        return {
            "total_analyses": 0,
            "recurring_signals": [],
            "recurring_gaps": [],
            "weak_categories": [],
        }

    total = len(history)

    signal_counter = Counter()
    gap_counter = Counter()
    category_scores = {}

    for analysis in history:

        # ---------------------------------------------
        # Signals
        # ---------------------------------------------

        signal = analysis.get(
            "signal",
            "",
        )

        if signal:
            signal_counter[signal] += 1

        # ---------------------------------------------
        # Missing evidence
        # ---------------------------------------------

        missing = analysis.get(
            "missing",
            [],
        )

        if isinstance(missing, list):
            for item in missing:
                if item:
                    gap_counter[str(item)] += 1

        # ---------------------------------------------
        # Category scores
        # ---------------------------------------------

        breakdown = analysis.get(
            "breakdown",
            {},
        )

        if isinstance(breakdown, dict):

            for category, score in breakdown.items():

                try:
                    score = float(score)
                except (
                    ValueError,
                    TypeError,
                ):
                    continue

                if category not in category_scores:
                    category_scores[category] = []

                category_scores[category].append(
                    score
                )

    # =================================================
    # RECURRING SIGNALS
    # =================================================

    recurring_signals = []

    for signal, count in signal_counter.most_common():

        if count >= 2:

            recurring_signals.append(
                {
                    "name": signal,
                    "count": count,
                    "total": total,
                    "percentage": round(
                        (count / total) * 100
                    ),
                }
            )

    # =================================================
    # RECURRING GAPS
    # =================================================

    recurring_gaps = []

    for gap, count in gap_counter.most_common():

        if count >= 2:

            recurring_gaps.append(
                {
                    "name": gap,
                    "count": count,
                    "total": total,
                    "percentage": round(
                        (count / total) * 100
                    ),
                }
            )

    # =================================================
    # WEAK CATEGORIES
    # =================================================

    weak_categories = []

    for category, scores in category_scores.items():

        if not scores:
            continue

        average = sum(scores) / len(scores)

        weak_count = sum(
            1
            for score in scores
            if score < 50
        )

        if weak_count >= 2:

            weak_categories.append(
                {
                    "name": category,
                    "average": round(
                        average
                    ),
                    "weak_count": weak_count,
                    "total": len(scores),
                }
            )

    weak_categories.sort(
        key=lambda item: (
            -item["weak_count"],
            item["average"],
        )
    )

    return {
        "total_analyses": total,
        "recurring_signals": recurring_signals[
            :5
        ],
        "recurring_gaps": recurring_gaps[
            :8
        ],
        "weak_categories": weak_categories[
            :6
        ],
    }


def get_pattern_summary(history):
    """
    Generate a short human-readable summary
    of the strongest recurring pattern.
    """

    patterns = detect_patterns(history)

    if patterns["total_analyses"] < 2:
        return (
            "Complete at least two analyses "
            "to detect recurring patterns."
        )

    if patterns["weak_categories"]:

        strongest = patterns[
            "weak_categories"
        ][0]

        return (
            f"{strongest['name']} appears as a "
            f"recurring weakness across "
            f"{strongest['weak_count']} analyses."
        )

    if patterns["recurring_gaps"]:

        strongest = patterns[
            "recurring_gaps"
        ][0]

        return (
            f"{strongest['name']} is a recurring "
            f"evidence gap across "
            f"{strongest['count']} analyses."
        )

    if patterns["recurring_signals"]:

        strongest = patterns[
            "recurring_signals"
        ][0]

        return (
            f"{strongest['name']} is a recurring "
            f"signal across "
            f"{strongest['count']} analyses."
        )

    return (
        "No strong recurring pattern has emerged yet."
    )