import asyncio
import flet as ft

from components.ui import (
    text, mono, section_header, create_navbar, animated_grid_background, panel,
    hairline, chip,
    BG, BG_CARD, BG_SURFACE, BORDER, BORDER_CARD, BORDER_ACCENT,
    TEXT_PRIMARY, TEXT_HEADING, TEXT_BODY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DIM,
    CYAN, CYAN_LIGHT, CYAN_MUTED, CYAN_GLOW, CYAN_DARK,
    PURPLE, PURPLE_LIGHT, PURPLE_DARK,
    SERIF, ANIM_REVEAL, RADIUS_MD, RADIUS_LG,
)
from components.graph import build_evidence_graph

try:
    from services.history import get_analysis_history
except Exception:  # pragma: no cover - defensive
    def get_analysis_history():
        return []


def show_landing(page: ft.Page, on_analyze, on_insights=None):
    page.controls.clear()

    MUTED = "#948EA0"
    DIM = "#615C6B"

    # ---------------------------------------------------------
    # SCROLLABLE BODY (declared early so nav can target it)
    # ---------------------------------------------------------

    body = ft.Column(
        expand=True, spacing=0, scroll=ft.ScrollMode.AUTO,
    )

    async def _do_scroll(key):
        try:
            await body.scroll_to(scroll_key=key, duration=620,
                                 curve=ft.AnimationCurve.EASE_IN_OUT)
        except Exception:
            pass

    def scroll_to(key):
        page.run_task(_do_scroll, key)

    def handle_section(section):
        if section == "insights":
            if on_insights:
                on_insights()
        elif section == "product":
            scroll_to("product")
        elif section == "how_it_works":
            scroll_to("how")

    navigation = create_navbar(
        on_get_started=on_analyze, page=page, is_landing=True,
        on_section_click=handle_section,
    )
    navigation.opacity = 0
    navigation.animate_opacity = ft.Animation(600, ft.AnimationCurve.EASE_OUT)

    # ---------------------------------------------------------
    # HERO TEXT — editorial serif
    # ---------------------------------------------------------

    def line(control, dy=0.14):
        return ft.Container(
            content=control, opacity=0, offset=ft.Offset(0, dy),
            animate_opacity=ft.Animation(760, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_offset=ft.Animation(760, ft.AnimationCurve.EASE_OUT_CUBIC),
        )

    eyebrow = line(ft.Container(
        padding=ft.Padding(top=8, right=13, bottom=8, left=13),
        border_radius=20, bgcolor="#0C1418",
        border=ft.Border.all(1, "#1E3A40"),
        content=ft.Row(tight=True, spacing=8, controls=[
            ft.Container(width=6, height=6, border_radius=3, bgcolor=CYAN),
            mono("Rejection intelligence", 10, "#9FD8E1"),
        ]),
    ))

    l_rejection = line(ft.Text(
        "REJECTION", size=66, font_family=SERIF, weight=ft.FontWeight.BOLD,
        color="#F4F2F7", style=ft.TextStyle(letter_spacing=0.5)))
    l_has = line(ft.Text(
        "HAS", size=34, font_family=SERIF, weight=ft.FontWeight.W_400,
        color="#8A8496", style=ft.TextStyle(letter_spacing=1)))
    l_signals = line(ft.Text(
        "SIGNALS.", size=72, font_family=SERIF, weight=ft.FontWeight.BOLD,
        color=CYAN, style=ft.TextStyle(letter_spacing=0.5)))

    supporting = line(text(
        "REFRACT turns your application history into evidence-backed signals, "
        "recurring patterns, and a clearer direction for what to improve next.",
        16, MUTED))

    cta = ft.Container(
        padding=ft.Padding(top=15, right=20, bottom=15, left=20),
        border_radius=12, bgcolor=CYAN, border=ft.Border.all(1, CYAN_LIGHT),
        on_click=lambda e: on_analyze(e),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=26,
                            color=ft.Colors.with_opacity(0.24, CYAN),
                            offset=ft.Offset(0, 6)),
        content=ft.Row(tight=True, spacing=12, controls=[
            text("Analyze an application", 14, "#04161A", ft.FontWeight.BOLD),
            text("→", 18, "#04161A", ft.FontWeight.BOLD),
        ]),
    )

    def _cta_hover(e):
        h = e.data == "true"
        cta.bgcolor = CYAN_LIGHT if h else CYAN
        cta.scale = 1.02 if h else 1.0
        cta.shadow = ft.BoxShadow(
            spread_radius=1 if h else 0, blur_radius=42 if h else 26,
            color=ft.Colors.with_opacity(0.46 if h else 0.24, CYAN),
            offset=ft.Offset(0, 8 if h else 6))
        cta.update()

    cta.on_hover = _cta_hover
    cta_wrap = line(cta)

    trust = line(text(
        "Evidence-first  ·  Confidence-aware  ·  Privacy-conscious", 11, DIM))

    hero_text = ft.Container(width=620, content=ft.Column(spacing=18, controls=[
        eyebrow,
        ft.Column(spacing=-2, controls=[l_rejection, l_has, l_signals]),
        supporting, cta_wrap, trust,
    ]))

    # ---------------------------------------------------------
    # EVIDENCE TRAJECTORY CARD — compact
    # ---------------------------------------------------------

    history = list(reversed(get_analysis_history() or []))
    scores = [h.get("overall_score", 0) for h in history if isinstance(h, dict)]
    if len(scores) >= 3:
        series = scores[-10:]
        end_label = f"APPLICATION {len(scores):02d}"
    else:
        series = [61, 52, 58, 40, 47, 33, 44, 38, 52, 46]
        end_label = "LATEST"

    graph = build_evidence_graph(series, width=352, height=132, accent=CYAN)

    graph_card = ft.Container(
        width=404, padding=20, border_radius=RADIUS_LG,
        bgcolor=BG_CARD, border=ft.Border.all(1, BORDER_CARD),
        opacity=0, offset=ft.Offset(0.05, 0.03),
        animate_opacity=ft.Animation(900, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_offset=ft.Animation(900, ft.AnimationCurve.EASE_OUT_CUBIC),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=40,
                            color=ft.Colors.with_opacity(0.05, CYAN),
                            offset=ft.Offset(0, 10)),
        content=ft.Column(spacing=9, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                mono("Evidence trajectory", 9, CYAN_LIGHT),
                mono("Application history", 8, DIM),
            ]),
            text("Your signal changes.", 19, TEXT_HEADING, ft.FontWeight.BOLD),
            ft.Container(content=graph, alignment=ft.Alignment(0, 0)),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                mono("APPLICATION 01", 8, DIM),
                mono(end_label, 8, DIM),
            ]),
        ]),
    )

    # hero_text (fixed) — flexible spacer — graph card — fixed right gap.
    # The spacer keeps the card beside the hero on wide screens; the trailing
    # gap pulls it in from the right edge so it doesn't hug the border.
    hero = ft.Container(
        key=ft.ScrollKey("top"),
        padding=ft.Padding(top=34, right=72, bottom=48, left=72),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                hero_text,
                ft.Container(expand=True),
                graph_card,
                ft.Container(width=16),
            ],
        ),
    )

    # ---------------------------------------------------------
    # SECTION: PRODUCT
    # ---------------------------------------------------------

    def feature(title, body_text):
        return ft.Container(
            expand=True, padding=22, border_radius=RADIUS_MD,
            bgcolor=BG_CARD, border=ft.Border.all(1, BORDER_CARD),
            content=ft.Column(spacing=8, controls=[
                text(title, 15, TEXT_HEADING, ft.FontWeight.BOLD),
                text(body_text, 12.5, TEXT_MUTED),
            ]),
        )

    product = ft.Container(
        key=ft.ScrollKey("product"),
        padding=ft.Padding(top=52, right=72, bottom=52, left=72),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
        content=ft.Column(spacing=22, controls=[
            section_header("Product", CYAN),
            ft.Text("Evidence, not vibes.", size=38, font_family=SERIF,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            text("REFRACT reads your resume and a target job description, then converts "
                 "what it finds into explainable signals — no black-box scoring.",
                 15, TEXT_SECONDARY),
            ft.Container(height=6),
            ft.Row(spacing=18, controls=[
                feature("Explainable signals",
                        "Every signal is traced back to concrete evidence in your resume "
                        "and the job requirements."),
                feature("Priority engine",
                        "The gaps that matter most are ranked HIGH / MEDIUM / LOW with a "
                        "clear next action."),
                feature("Role direction",
                        "See where your current evidence actually points, plus credible "
                        "alternative directions."),
            ]),
            ft.Row(spacing=18, controls=[
                feature("Personal roadmap",
                        "A practical, ordered sequence for closing your strongest gaps."),
                feature("Application comparison",
                        "Track score, confidence and category movement across analyses."),
                feature("Pattern detection",
                        "Recurring gaps and weak categories surface across your history."),
            ]),
        ]),
    )

    # ---------------------------------------------------------
    # SECTION: HOW IT WORKS
    # ---------------------------------------------------------

    def step_card(num, title, body_text):
        return ft.Container(
            expand=True, padding=22, border_radius=RADIUS_MD,
            bgcolor=BG_CARD, border=ft.Border.all(1, BORDER_CARD),
            content=ft.Column(spacing=13, controls=[
                ft.Container(width=42, height=42, border_radius=11, bgcolor=CYAN_GLOW,
                             border=ft.Border.all(1, BORDER_ACCENT),
                             alignment=ft.Alignment(0, 0),
                             content=mono(num, 12, CYAN_LIGHT)),
                text(title, 15, TEXT_HEADING, ft.FontWeight.BOLD),
                text(body_text, 12.5, TEXT_MUTED),
            ]),
        )

    how = ft.Container(
        key=ft.ScrollKey("how"),
        padding=ft.Padding(top=52, right=72, bottom=64, left=72),
        border=ft.Border(top=ft.BorderSide(1, BORDER)),
        content=ft.Column(spacing=22, controls=[
            section_header("How it works", CYAN),
            ft.Text("Three steps.", size=38, font_family=SERIF,
                    weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
            ft.Container(height=6),
            ft.Row(spacing=18, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                step_card("01", "Provide the evidence",
                          "Upload your resume and the job description. Optionally add a "
                          "rejection or feedback note."),
                step_card("02", "REFRACT compares",
                          "Requirements are matched against demonstrated evidence, "
                          "category by category, with a confidence estimate."),
                step_card("03", "Read the report",
                          "Move through overall signal, evidence strength, priorities, "
                          "role direction, roadmap, comparison and patterns."),
            ]),
            ft.Container(height=10),
            ft.Row(controls=[
                ft.Container(
                    padding=ft.Padding(top=14, right=20, bottom=14, left=20),
                    border_radius=12, border=ft.Border.all(1, BORDER_ACCENT),
                    bgcolor="transparent", on_click=lambda e: on_analyze(e),
                    animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                    shadow=ft.BoxShadow(spread_radius=0, blur_radius=14,
                                        color=ft.Colors.with_opacity(0.0, CYAN),
                                        offset=ft.Offset(0, 4)),
                    content=text("Start an analysis  →", 13, CYAN, ft.FontWeight.BOLD),
                ),
            ]),
        ]),
    )

    footer = ft.Container(
        padding=ft.Padding(top=15, right=72, bottom=15, left=72),
        border=ft.Border(top=ft.BorderSide(width=1, color=BORDER)),
        content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            text("Your rejection history has information.", 11, DIM),
            mono("REFRACT / 01", 9, "#4C4757"),
        ]),
    )

    body.controls = [hero, product, how, footer]

    # ---------------------------------------------------------
    # BACKGROUND + COMPOSE
    # ---------------------------------------------------------

    bg = animated_grid_background(page)

    page.add(ft.Stack(expand=True, controls=[
        bg,
        ft.Column(expand=True, spacing=0, controls=[navigation, body]),
    ]))
    page.update()

    async def reveal():
        try:
            await asyncio.sleep(0.1)
            navigation.opacity = 1
            navigation.update()
            await asyncio.sleep(0.14)
            for c in [eyebrow, l_rejection, l_has, l_signals,
                      supporting, cta_wrap, trust]:
                c.opacity = 1
                c.offset = ft.Offset(0, 0)
                c.update()
                await asyncio.sleep(0.09)
            graph_card.opacity = 1
            graph_card.offset = ft.Offset(0, 0)
            graph_card.update()
            pulse = (graph.data or {}).get("pulse") if graph.data else None
            if pulse:
                page.run_task(pulse)
        except Exception:
            return

    page.run_task(reveal)
