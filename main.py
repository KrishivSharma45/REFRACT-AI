import tempfile
from pathlib import Path

import flet as ft

from pages.landing import show_landing
from pages.analysis import show_analysis
from pages.results import show_results_flow
from pages.insights import show_insights
from services.parser import extract_text
from components.ui import toast


def _read_picked_file(picked):
    """Return extracted text for a picked file, working on desktop (path)
    and web (bytes) builds of Flet."""
    path = getattr(picked, "path", None)
    if path:
        return extract_text(path)

    data = getattr(picked, "bytes", None)
    if data:
        suffix = Path(getattr(picked, "name", "file.txt")).suffix or ".txt"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        return extract_text(tmp_path)

    raise ValueError(
        "Could not read the selected file. If you are running the web build, "
        "run the desktop app instead (flet run main.py)."
    )


def main(page: ft.Page):

    page.title = "REFRACT"
    page.bgcolor = "#08090D"
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK

    # =========================================================
    # FILE PICKER
    # =========================================================

    file_picker = ft.FilePicker()
    page.services.append(file_picker)

    selected_files = {
        "resume": None,
        "jd": None,
        "rejection": None,
    }

    # =========================================================
    # HOME
    # =========================================================

    def navigate_to_home(e=None):
        show_landing(
            page,
            on_analyze=navigate_to_analysis,
            on_insights=navigate_to_insights,
        )

    # =========================================================
    # INSIGHTS
    # =========================================================

    def navigate_to_insights(e=None):
        show_insights(
            page,
            on_home=navigate_to_home,
            on_new_analysis=navigate_to_analysis,
        )

    # =========================================================
    # RESULTS
    # =========================================================

    def navigate_to_results(e=None):

        try:

            resume_file = selected_files.get("resume")
            jd_file = selected_files.get("jd")
            rejection_file = selected_files.get("rejection")

            if resume_file is None or jd_file is None:
                toast(page, "Upload both a resume and a job description.", error=True)
                return

            resume_text = _read_picked_file(resume_file)
            jd_text = _read_picked_file(jd_file)

            rejection_text = ""
            if rejection_file is not None:
                rejection_text = _read_picked_file(rejection_file)

            page.run_task(
                show_results_flow,
                page,
                resume_text,
                jd_text,
                rejection_text,
                navigate_to_analysis,
                navigate_to_home,
            )

        except Exception as error:
            toast(page, f"Analysis error: {error}", error=True)

    # =========================================================
    # ANALYSIS PAGE
    # =========================================================

    def navigate_to_analysis(e=None):

        show_analysis(
            page,
            on_begin_analysis=navigate_to_results,
            file_picker=file_picker,
            selected_files=selected_files,
            on_home=navigate_to_home,
            on_insights=navigate_to_insights,
        )

    # =========================================================
    # START
    # =========================================================

    navigate_to_home()


if __name__ == "__main__":
    ft.run(main)