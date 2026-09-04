import asyncio
import flet as ft

from components.ui import (
    text, mono, section_header, ghost_button, primary_button,
    ambient_background, animated_grid_background, grid_background, create_navbar, hairline, chip,
    delta_badge, metric, panel,
    BG, BG_CARD, BG_SURFACE, BG_ELEVATED,
    CYAN, CYAN_LIGHT, CYAN_MUTED, CYAN_DIM, CYAN_GLOW,
    PURPLE, PURPLE_LIGHT, PURPLE_MUTED, PURPLE_DIM, PURPLE_GLOW,
    TEXT_PRIMARY, TEXT_HEADING, TEXT_BODY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DIM,
    BORDER, BORDER_CARD, BORDER_ACCENT,
    SUCCESS, ERROR, WARN,
    ANIM_FAST, ANIM_NORMAL, ANIM_REVEAL,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, PAGE_PAD, SECTION_GAP,
)
from components.graph import build_evidence_graph

from services.history import get_analysis_history, compare_analyses
from services.patterns import detect_patterns, get_pattern_summary


def _score_color(score):
    try:
        score = float(score)
    except (TypeError, ValueError):
        score = 0
    if score >= 70:
        return SUCCESS
    if score >= 45:
        return WARN
    return ERROR


def _fmt_date(value):
    if not value:
        return "Unknown date"
    return str(value).replace("T", "  ·  ")


def show_insights(page: ft.Page, on_home, on_new_analysis):
    page.controls.clear()

    history = get_analysis_history()          # newest first
    patterns = detect_patterns(history)
    pattern_summary = get_pattern_summary(history)

    navbar = create_navbar(on_get_started=on_new_analysis, page=page,
                           is_landing=False, on_home_click=on_home)

    # ---------------------------------------------------------
    # EMPTY / INSUFFICIENT STATE
    # ---------------------------------------------------------

    if len(history) < 1:
        page.add(ft.Stack(expand=True, controls=[
            grid_background(),
            ft.Column(expand=True, spacing=0, controls=[
                navbar,
                ft.Container(expand=True, alignment=ft.Alignment(0, 0),
                             content=ft.Column(
                                 horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=14,
                                 controls=[
                                     section_header("Insights", CYAN),
                                     text("No analyses yet.", 30, TEXT_PRIMARY, ft.FontWeight.BOLD),
                                     text("Run your first REFRACT analysis to start building "
                                          "your evidence history.", 13, TEXT_MUTED),
                                     ft.Container(height=6),
                                     primary_button("Start analysis", on_new_analysis, width=220),
                                 ])),
            ]),
        ]))
        page.update()
        return

    # ---------------------------------------------------------
    # HEADER + KPI STRIP
    # ---------------------------------------------------------

    chrono = list(reversed(history))          # oldest -> newest
    scores = [h.get("overall_score", 0) for h in chrono if isinstance(h, dict)]
    latest = history[0]
    first = history[-1]
    total = len(history)
    avg_score = round(sum(scores) / len(scores)) if scores else 0
    lifetime_delta = (scores[-1] - scores[0]) if len(scores) >= 2 else 0

    header = ft.Container(
        opacity=0, offset=ft.Offset(0, 0.05),
        animate_opacity=ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_offset=ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC),
        content=ft.Column(spacing=8, controls=[
            section_header("Analytical command center", CYAN),
            text("Insights", 40, TEXT_PRIMARY, ft.FontWeight.BOLD),
            text("Your application history, turned into direction.", 14, TEXT_SECONDARY),
        ]),
    )

    kpi = panel(
        ft.Row(spacing=44, wrap=True, controls=[
            metric("Analyses", total, accent=TEXT_PRIMARY, value_size=28),
            metric("Average signal", f"{avg_score}%", accent=CYAN_LIGHT, value_size=28),
            metric("Latest signal", latest.get("signal", "—"),
                   sub=f"{latest.get('overall_score', 0)}% alignment",
                   accent=TEXT_PRIMARY, value_size=20),
            metric("Lifetime change", "", sub=delta_badge(lifetime_delta, "pts", 15),
                   accent=TEXT_PRIMARY, value_size=10),
        ]),
        padding=24,
    )

    # ---------------------------------------------------------
    # TRAJECTORY
    # ---------------------------------------------------------

    if len(scores) >= 2:
        g = build_evidence_graph(scores[-12:], width=880, height=190, accent=CYAN)
        gp = (g.data or {}).get("pulse") if g.data else None
        if gp:
            page.run_task(gp)
        trajectory = panel(ft.Column(spacing=14, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                mono("Evidence trajectory", 10, TEXT_MUTED),
                mono(f"{total} analyses on record", 9, TEXT_DIM),
            ]),
            ft.Row(scroll=ft.ScrollMode.AUTO, controls=[g]),
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                mono(_fmt_date(first.get("created_at")).split("·")[0].strip(), 9, TEXT_DIM),
                mono(_fmt_date(latest.get("created_at")).split("·")[0].strip(), 9, TEXT_DIM),
            ]),
        ]), padding=24)
    else:
        trajectory = panel(ft.Column(spacing=8, controls=[
            mono("Evidence trajectory", 10, TEXT_MUTED),
            text("Two or more analyses are needed to plot a trajectory.", 13, TEXT_MUTED),
        ]), padding=24)

    # ---------------------------------------------------------
    # TIMELINE (history as connected column)
    # ---------------------------------------------------------

    timeline_nodes = []
    shown_history = history[:10]
    for idx, item in enumerate(shown_history):
        is_last = idx == len(shown_history) - 1
        sc = item.get("overall_score", 0)
        timeline_nodes.append(ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START, spacing=16, controls=[
                ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
                    ft.Container(width=30, height=30, border_radius=15, bgcolor=PURPLE_GLOW,
                                 border=ft.Border.all(1, PURPLE_DIM), alignment=ft.Alignment(0, 0),
                                 content=text(str(total - idx).zfill(2), 10, PURPLE_LIGHT, ft.FontWeight.BOLD)),
                    ft.Container(width=1, height=(0 if is_last else 40), bgcolor=BORDER),
                ]),
                ft.Container(
                    expand=True,
                    padding=ft.Padding(left=0, top=4, right=0, bottom=(0 if is_last else 18)),
                    content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                        ft.Column(spacing=3, expand=True, controls=[
                            text(str(item.get("signal", "Role Alignment")), 14, TEXT_PRIMARY, ft.FontWeight.BOLD),
                            mono(_fmt_date(item.get("created_at")), 9, TEXT_DIM, spacing=1.0),
                        ]),
                        text(f"{sc}%", 18, _score_color(sc), ft.FontWeight.BOLD),
                    ]),
                ),
            ],
        ))

    more_note = []
    if len(history) > len(shown_history):
        more_note = [ft.Container(
            padding=ft.Padding(left=0, top=12, right=0, bottom=0),
            content=mono(f"+ {len(history) - len(shown_history)} earlier analyses", 9, TEXT_DIM))]

    timeline = panel(ft.Column(spacing=0, controls=[
        mono("Application history", 10, CYAN), ft.Container(height=12),
        *timeline_nodes, *more_note,
    ]), padding=26)

    # ---------------------------------------------------------
    # COMPARISON PANEL
    # ---------------------------------------------------------

    options = [
        ft.dropdown.Option(str(i),
                           f'{it.get("signal", "Analysis")} · {it.get("overall_score", 0)}%')
        for i, it in enumerate(history)
    ]

    current_dd = ft.Dropdown(
        label="Current", value="0", options=list(options), width=280,
        bgcolor=BG_SURFACE, border_color=BORDER_CARD, focused_border_color=CYAN,
        color=TEXT_PRIMARY, text_size=13,
    )
    previous_dd = ft.Dropdown(
        label="Compare against", value=("1" if len(history) >= 2 else "0"),
        options=list(options), width=280,
        bgcolor=BG_SURFACE, border_color=BORDER_CARD, focused_border_color=CYAN,
        color=TEXT_PRIMARY, text_size=13,
    )

    comparison_body = ft.Column(spacing=14)

    def render_comparison(e=None):
        try:
            ci = int(current_dd.value)
            pi = int(previous_dd.value)
        except (TypeError, ValueError):
            comparison_body.controls = [text("Select two analyses to compare.", 12, TEXT_MUTED)]
            page.update()
            return

        if ci == pi:
            comparison_body.controls = [
                text("Select two different analyses to compare.", 12, TEXT_MUTED)]
            page.update()
            return

        comp = compare_analyses(history[ci], history[pi])
        if not comp:
            comparison_body.controls = [text("Comparison could not be generated.", 12, TEXT_MUTED)]
            page.update()
            return

        sc = comp.get("score_change", 0)
        cc = comp.get("confidence_change", 0)
        cur = comp.get("current_score", 0)
        prev = comp.get("previous_score", 0)

        cat_rows = []
        for it in comp.get("category_changes", [])[:8]:
            ch = it.get("change", 0)
            cat_rows.append(ft.Container(
                padding=ft.Padding(left=0, top=10, right=0, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(expand=True, content=text(str(it.get("category", "")), 13, TEXT_BODY)),
                    ft.Container(width=52, alignment=ft.Alignment(1, 0),
                                content=text(f"{round(it.get('previous', 0))}%", 12, TEXT_MUTED)),
                    ft.Container(width=44, alignment=ft.Alignment(0, 0), content=delta_badge(ch, "", 12)),
                    ft.Container(width=52, alignment=ft.Alignment(1, 0),
                                content=text(f"{round(it.get('current', 0))}%", 12, TEXT_PRIMARY, ft.FontWeight.BOLD)),
                ]),
            ))
        if not cat_rows:
            cat_rows = [text("No category changes detected.", 12, TEXT_MUTED)]

        comparison_body.controls = [
            ft.Row(spacing=0, controls=[
                ft.Container(expand=1, content=ft.Column(spacing=4, controls=[
                    mono("Selected baseline", 9, TEXT_MUTED),
                    ft.Text(f"{prev}%", size=30, color=TEXT_SECONDARY, weight=ft.FontWeight.BOLD),
                ])),
                ft.Container(width=1, height=58, bgcolor=BORDER),
                ft.Container(expand=1, alignment=ft.Alignment(0, 0), content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
                    controls=[mono("Change", 9, TEXT_MUTED), delta_badge(sc, "pts", 17)])),
                ft.Container(width=1, height=58, bgcolor=BORDER),
                ft.Container(expand=1, alignment=ft.Alignment(1, 0), content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4,
                    controls=[mono("Selected current", 9, TEXT_MUTED),
                              ft.Text(f"{cur}%", size=30, color=CYAN_LIGHT, weight=ft.FontWeight.BOLD)])),
            ]),
            hairline(),
            ft.Row(spacing=30, controls=[
                ft.Column(spacing=5, controls=[
                    mono("Confidence change", 9, TEXT_MUTED), delta_badge(cc, "pts", 14)]),
                ft.Column(spacing=5, controls=[
                    mono("Current signal", 9, TEXT_MUTED),
                    text(str(comp.get("current_signal", "Role Alignment")), 14,
                         TEXT_PRIMARY, ft.FontWeight.BOLD)]),
            ]),
            hairline(),
            mono("What changed", 9, CYAN),
            ft.Column(spacing=0, controls=cat_rows),
        ]
        page.update()

    compare_btn = ghost_button("Compare", render_comparison)

    comparison_panel = panel(ft.Column(spacing=16, controls=[
        mono("Compare applications", 10, CYAN),
        text("See what moved between any two analyses.", 13, TEXT_SECONDARY),
        ft.Row(spacing=14, wrap=True, controls=[current_dd, previous_dd, compare_btn]),
        hairline(),
        comparison_body,
    ]), padding=26)

    # ---------------------------------------------------------
    # PATTERNS
    # ---------------------------------------------------------

    def freq_rows(items, fmt):
        out = []
        for it in items[:6]:
            out.append(ft.Container(
                padding=ft.Padding(left=0, top=10, right=0, bottom=10),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                content=ft.Row(controls=[
                    ft.Container(expand=True, content=text(str(it.get("name", "Unknown")), 13, TEXT_BODY)),
                    text(fmt(it), 11, TEXT_MUTED, ft.FontWeight.BOLD),
                ]),
            ))
        return out or [text("None detected yet.", 12, TEXT_MUTED)]

    if patterns.get("total_analyses", 0) < 2:
        patterns_panel = panel(ft.Column(spacing=8, controls=[
            mono("Recurring patterns", 10, CYAN),
            text("Run at least two analyses to surface recurring gaps and weak categories.",
                 13, TEXT_MUTED),
        ]), padding=26)
    else:
        _pg = patterns.get("recurring_gaps", [])[:6]
        _pw = patterns.get("weak_categories", [])[:6]
        _ps = patterns.get("recurring_signals", [])[:6]
        _rows_max = max(len(_pg), len(_pw), len(_ps), 1)
        _card_h = 78 + _rows_max * 40

        def freq_card(label, items, fmt):
            return ft.Container(
                expand=1, height=_card_h, padding=24, border_radius=RADIUS_LG,
                bgcolor=BG_CARD, border=ft.Border.all(1, BORDER_CARD),
                content=ft.Column(spacing=0, controls=[
                    mono(label, 9, CYAN), ft.Container(height=6),
                    *freq_rows(items, fmt),
                ]),
            )

        patterns_panel = ft.Column(spacing=SECTION_GAP, controls=[
            panel(ft.Column(spacing=6, controls=[
                mono("Recurring patterns", 10, CYAN),
                text(pattern_summary, 18, TEXT_PRIMARY, ft.FontWeight.BOLD),
                mono(f"{patterns.get('total_analyses', 0)} analyses analysed", 9, TEXT_DIM),
            ]), padding=24),
            ft.Row(
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    freq_card("Recurring gaps", patterns.get("recurring_gaps", []),
                              lambda it: f"{it.get('count', 0)}/{it.get('total', 0)}"),
                    freq_card("Weak categories", patterns.get("weak_categories", []),
                              lambda it: f"avg {it.get('average', 0)}%"),
                    freq_card("Recurring signals", patterns.get("recurring_signals", []),
                              lambda it: f"{it.get('count', 0)}x"),
                ],
            ),
        ])

    # ---------------------------------------------------------
    # LAYOUT
    # ---------------------------------------------------------

    sections = [
        header,
        kpi,
        trajectory,
        ft.Row(spacing=24, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
            ft.Container(expand=5, content=comparison_panel),
            ft.Container(expand=4, content=timeline),
        ]),
        patterns_panel,
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            mono("REFRACT · evidence first · confidence aware", 9, TEXT_DIM),
            primary_button("Start new analysis", on_new_analysis),
        ]),
    ]

    for s in sections[1:]:
        s.opacity = 0
        s.offset = ft.Offset(0, 0.04)
        s.animate_opacity = ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC)
        s.animate_offset = ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC)

    content = ft.Column(
        spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, expand=True, controls=sections,
    )

    page.add(ft.Stack(expand=True, controls=[
        animated_grid_background(page),
        ft.Column(expand=True, spacing=0, controls=[
            navbar,
            ft.Container(expand=True,
                         padding=ft.Padding(left=PAGE_PAD, top=26, right=PAGE_PAD, bottom=24),
                         content=content),
        ]),
    ]))
    page.update()

    if len(history) >= 2:
        render_comparison()

    async def reveal():
        try:
            await asyncio.sleep(0.12)
            for s in sections:
                s.opacity = 1
                s.offset = ft.Offset(0, 0)
                s.update()
                await asyncio.sleep(0.08)
        except Exception:
            return

    page.run_task(reveal)
