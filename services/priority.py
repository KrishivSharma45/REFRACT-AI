from services.analyzer import CATEGORIES


def build_priority_items(breakdown, missing):
    """
    Convert analyzer category results into ranked improvement priorities.
    Higher gap + higher category weight = higher priority.
    """

    missing_text = " ".join(missing).lower() if isinstance(missing, list) else str(missing).lower()

    items = []

    for category, score in breakdown.items():
        score = float(score)

        # Larger gap means more room for improvement.
        gap = max(0, 100 - score)

        if gap >= 60:
            priority = "HIGH"
        elif gap >= 30:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        category_lower = category.lower()

        # Try to identify a missing evidence keyword related to this category.
        category_missing = []

        for word in missing_text.split():
            cleaned = word.strip(".,:;()[]{}\"'")
            if len(cleaned) >= 3 and (
                cleaned in category_lower
                or category_lower in cleaned
            ):
                category_missing.append(cleaned)

        if category_missing:
            gap_text = ", ".join(dict.fromkeys(category_missing[:3]))
        else:
            gap_text = "stronger evidence"

        if priority == "HIGH":
            action = f"Strengthen {category.lower()} evidence. Focus on {gap_text}."
        elif priority == "MEDIUM":
            action = f"Add stronger {category.lower()} evidence, especially around {gap_text}."
        else:
            action = f"Keep building {category.lower()} evidence."

        items.append(
            {
                "category": category,
                "score": round(score),
                "gap": round(gap),
                "priority": priority,
                "action": action,
            }
        )

    priority_order = {
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 2,
    }

    items.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            -item["gap"],
        )
    )

    return items


def get_top_priorities(breakdown, missing, limit=5):
    items = build_priority_items(breakdown, missing)
    return items[:limit]