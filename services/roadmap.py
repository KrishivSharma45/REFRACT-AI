def _normalise(value):
    return str(value or "").strip().lower()


def build_roadmap(
    breakdown,
    priorities=None,
    role_direction=None,
):
    """
    Build a practical improvement roadmap from
    REFRACT evidence gaps.

    This is an evidence-based improvement plan,
    not a prediction of hiring outcomes.
    """

    breakdown = breakdown or {}
    priorities = priorities or []

    roadmap = []

    # ---------------------------------------------------------
    # STEP 1 — FIX THE BIGGEST GAP
    # ---------------------------------------------------------

    if priorities:

        top_priority = priorities[0]

        category = top_priority.get(
            "category",
            "core evidence",
        )

        action = top_priority.get(
            "action",
            "Strengthen this area.",
        )

        roadmap.append(
            {
                "step": 1,
                "title": f"Strengthen {category}",
                "action": action,
                "type": "Priority",
            }
        )

    # ---------------------------------------------------------
    # STEP 2 — STRENGTHEN THE WEAKEST CATEGORY
    # ---------------------------------------------------------

    weakest_category = None
    weakest_score = None

    for category, score in breakdown.items():

        try:
            score = float(score)
        except (
            ValueError,
            TypeError,
        ):
            continue

        if (
            weakest_score is None
            or score < weakest_score
        ):
            weakest_category = category
            weakest_score = score

    if weakest_category:

        roadmap.append(
            {
                "step": 2,
                "title": f"Build {weakest_category} evidence",
                "action": (
                    f"Add concrete proof of "
                    f"{_normalise(weakest_category)} "
                    f"through projects, coursework, "
                    f"achievements, or measurable outcomes."
                ),
                "type": "Evidence",
            }
        )

    # ---------------------------------------------------------
    # STEP 3 — ALIGN WITH ROLE DIRECTION
    # ---------------------------------------------------------

    role_name = "your target role"

    if role_direction:

        if isinstance(
            role_direction,
            dict,
        ):
            role_name = role_direction.get(
                "role",
                role_name,
            )

        else:
            role_name = str(
                role_direction
            )

    roadmap.append(
        {
            "step": 3,
            "title": f"Increase {role_name} alignment",
            "action": (
                f"Prioritize projects, skills, and "
                f"resume evidence that directly support "
                f"{role_name}."
            ),
            "type": "Alignment",
        }
    )

    return roadmap


def get_roadmap_summary(roadmap):
    """
    Return a short summary of the improvement roadmap.
    """

    if not roadmap:

        return (
            "Complete an analysis to generate "
            "a personal improvement roadmap."
        )

    first_step = roadmap[0]

    return (
        f'Your next priority is '
        f'{first_step["title"]}.'
    )