import json
import os
import tempfile
from pathlib import Path
from datetime import datetime


# Resolve relative to the project root so history works regardless of CWD
# (flet run, flet web, packaged app, tests).
HISTORY_FILE = Path(__file__).resolve().parent.parent / "refract_history.json"


def _load_history():
    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def _save_history(history):
    """
    Write history atomically: build the new file fully on disk, then
    replace the old one in a single filesystem op. A crash or forced
    quit mid-write (this app gets killed/restarted a lot during
    development) can otherwise leave a truncated, unreadable
    refract_history.json — which _load_history() then silently treats
    as empty, discarding the user's whole analysis history.
    """

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        dir=HISTORY_FILE.parent,
        prefix=".refract_history_",
        suffix=".tmp",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(
                history,
                file,
                indent=2,
                ensure_ascii=False,
            )

        os.replace(tmp_path, HISTORY_FILE)

    finally:
        # os.replace already removed it on success; this only cleans up
        # a leftover temp file if the write/replace above failed.
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def save_analysis(result):
    """
    Store a completed REFRACT analysis locally.

    Only analysis results are stored.
    Original resume/JD document text is not stored.
    """

    history = _load_history()

    entry = {
        "id": datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        ),
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "signal": result.get(
            "signal",
            "Role Alignment",
        ),
        "confidence": result.get(
            "confidence",
            0,
        ),
        "overall_score": result.get(
            "overall_score",
            0,
        ),
        "matched": result.get(
            "matched",
            [],
        ),
        "missing": result.get(
            "missing",
            [],
        ),
        "breakdown": result.get(
            "breakdown",
            {},
        ),
    }

    history.append(entry)

    # Keep the local history lightweight.
    history = history[-20:]

    _save_history(history)

    return entry


def get_analysis_history():
    """Return saved analyses, newest first."""

    history = _load_history()

    return list(reversed(history))


def get_latest_analysis():
    """Return the most recent analysis."""

    history = get_analysis_history()

    if not history:
        return None

    return history[0]


def get_previous_analysis():
    """Return the analysis before the latest one."""

    history = get_analysis_history()

    if len(history) < 2:
        return None

    return history[1]


def compare_analyses(current, previous):
    """
    Compare two saved analyses.

    Returns score/signal/category changes.
    """

    if not current or not previous:
        return None

    current_score = current.get(
        "overall_score",
        0,
    )

    previous_score = previous.get(
        "overall_score",
        0,
    )

    current_confidence = current.get(
        "confidence",
        0,
    )

    previous_confidence = previous.get(
        "confidence",
        0,
    )

    current_breakdown = current.get(
        "breakdown",
        {},
    )

    previous_breakdown = previous.get(
        "breakdown",
        {},
    )

    categories = sorted(
        set(current_breakdown)
        | set(previous_breakdown)
    )

    category_changes = []

    for category in categories:
        old_score = previous_breakdown.get(
            category,
            0,
        )

        new_score = current_breakdown.get(
            category,
            0,
        )

        change = new_score - old_score

        category_changes.append(
            {
                "category": category,
                "previous": old_score,
                "current": new_score,
                "change": change,
            }
        )

    category_changes.sort(
        key=lambda item: abs(
            item["change"]
        ),
        reverse=True,
    )

    return {
        "score_change": current_score - previous_score,
        "previous_score": previous_score,
        "current_score": current_score,
        "confidence_change": (
            current_confidence
            - previous_confidence
        ),
        "previous_signal": previous.get(
            "signal",
            "Role Alignment",
        ),
        "current_signal": current.get(
            "signal",
            "Role Alignment",
        ),
        "category_changes": category_changes,
    }


def clear_history():
    """Delete all locally stored analysis history."""

    if HISTORY_FILE.exists():
        try:
            HISTORY_FILE.unlink()
        except OSError:
            pass