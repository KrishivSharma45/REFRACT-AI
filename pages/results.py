import asyncio
import flet as ft

from components.ui import (
    text, mono, section_header, primary_button, ghost_button,
    ambient_background, animated_grid_background, grid_background, create_navbar, hairline, chip,
    delta_badge, metric, panel,
    BG, BG_CARD, BG_SURFACE, BG_ELEVATED, BG_INPUT,
    CYAN, CYAN_LIGHT, CYAN_MUTED, CYAN_DIM, CYAN_GLOW,
    PURPLE, PURPLE_LIGHT, PURPLE_MUTED, PURPLE_DIM, PURPLE_GLOW,
    TEXT_PRIMARY, TEXT_HEADING, TEXT_BODY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DIM,
    BORDER, BORDER_CARD, BORDER_ACCENT,
    SUCCESS, ERROR, WARN,
    ANIM_FAST, ANIM_NORMAL, ANIM_REVEAL,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, PAGE_PAD, SECTION_GAP,
)
from components.graph import build_evidence_graph

from services.analyzer import analyze_application
from services.priority import get_top_priorities
from services.evidence import analyze_evidence_strength, get_evidence_summary
from services.history import save_analysis, get_analysis_history, compare_analyses
from services.role_direction import detect_role_directions, get_primary_role_direction
from services.roadmap import build_roadmap, get_roadmap_summary
from services.patterns import detect_patterns, get_pattern_summary


TRANSPARENT = "#00000000"


def strength_color(strength):
    return {
        "Strong": SUCCESS,
        "Moderate": CYAN,
        "Weak": WARN,
        "Missing": ERROR,
    }.get(strength, TEXT_MUTED)


def priority_color(p):
    return {"HIGH": ERROR, "MEDIUM": WARN, "LOW": TEXT_MUTED}.get(p, TEXT_MUTED)


def wide_scroll(control):
    """Wrap a fixed-width visual so it never forces page overflow."""
    return ft.Row(scroll=ft.ScrollMode.AUTO, controls=[control])


async def show_results_flow(
    page: ft.Page,
    resume_text="",
    jd_text="",
    rejection_text="",
    on_new_analysis=None,
    on_home=None,
):
    page.controls.clear()

    # animated meters: list of (fill_container, ref_width, ratio)
    animated_bars = []

    def bar(pct, color=CYAN, ref_width=260, height=6, track=BG_ELEVATED):
        try:
            r = max(0.0, min(1.0, float(pct) / 100.0))
        except (TypeError, ValueError):
            r = 0.0
        fill = ft.Container(
            width=0, height=height, border_radius=height, bgcolor=color,
            animate=ft.Animation(ANIM_REVEAL + 150, ft.AnimationCurve.EASE_OUT_CUBIC),
        )
        animated_bars.append((fill, ref_width, r))
        return ft.Container(
            width=ref_width, height=height, border_radius=height, bgcolor=track,
            content=ft.Row(spacing=0, controls=[fill]),
        )

    # ---------------------------------------------------------
    # LOADING
    # ---------------------------------------------------------

    steps = [
        "Parsing evidence",
        "Comparing requirements",
        "Detecting signals",
        "Weighing confidence",
        "Composing report",
    ]

    step_rows = []
    for s in steps:
        step_rows.append(
            ft.Row(tight=True, spacing=12, controls=[
                ft.Container(width=16, alignment=ft.Alignment(0, 0),
                             content=text("○", 11, TEXT_MUTED)),
                text(s, 13, TEXT_MUTED),
            ])
        )

    progress = ft.Container(width=0, height=2, bgcolor=CYAN, border_radius=2,
                            animate=ft.Animation(320, ft.AnimationCurve.EASE_OUT))
    progress_track = ft.Container(width=320, height=2, bgcolor=BG_ELEVATED,
                                  border_radius=2, content=ft.Row(spacing=0, controls=[progress]))

    loading = ft.Container(
        expand=True, alignment=ft.Alignment(0, 0),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20,
            controls=[
                section_header("Analyzing evidence", CYAN),
                text("Finding the signal.", 34, TEXT_PRIMARY, ft.FontWeight.BOLD),
                ft.Container(height=4),
                ft.Column(spacing=13, horizontal_alignment=ft.CrossAxisAlignment.START,
                          controls=step_rows),
                ft.Container(height=10),
                progress_track,
            ],
        ),
    )

    page.add(ft.Stack(expand=True, controls=[grid_background(), loading]))
    page.update()

    for i in range(len(steps)):
        if i > 0:
            step_rows[i - 1].controls[0].content = text("✓", 11, SUCCESS)
            step_rows[i - 1].controls[1].color = TEXT_SECONDARY
        step_rows[i].controls[0].content = ft.ProgressRing(
            width=13, height=13, stroke_width=2, color=CYAN)
        step_rows[i].controls[1].color = TEXT_PRIMARY
        progress.width = 320 * ((i + 1) / len(steps))
        page.update()
        await asyncio.sleep(0.28)

    # ---------------------------------------------------------
    # RUN ANALYSIS
    # ---------------------------------------------------------

    try:
        result = analyze_application(resume_text, jd_text, rejection_text)
        breakdown = result.get("breakdown", {})
        save_analysis(result)
    except Exception as error:
        page.controls.clear()
        page.add(ft.Stack(expand=True, controls=[
            grid_background(),
            ft.Container(
                expand=True, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER, spacing=14,
                    controls=[
                        section_header("Analysis failed", ERROR),
                        text("Something went wrong.", 28, TEXT_HEADING, ft.FontWeight.BOLD),
                        text(str(error), 13, ERROR),
                        ghost_button("Back home", lambda e: on_home and on_home(e)),
                    ],
                ),
            ),
        ]))
        page.update()
        return

    for r in step_rows:
        r.controls[0].content = text("✓", 11, SUCCESS)
        r.controls[1].color = TEXT_SECONDARY
    progress.width = 320
    page.update()
    await asyncio.sleep(0.22)

    # ---------------------------------------------------------
    # DERIVE DATA
    # ---------------------------------------------------------

    signal = result.get("signal", "Role Alignment")
    confidence = int(result.get("confidence", 0) or 0)
    overall_score = int(result.get("overall_score", confidence) or 0)
    reason = result.get("reason", "No explanation available.")
    matched = result.get("matched", [])
    missing = result.get("missing", [])
    breakdown = result.get("breakdown", {})

    evidence_results = analyze_evidence_strength(resume_text, jd_text, matched, missing)
    evidence_summary = get_evidence_summary(evidence_results)

    try:
        priorities = get_top_priorities(breakdown, missing, limit=6)
    except Exception:
        priorities = []

    role_directions = detect_role_directions(breakdown)
    primary_role = get_primary_role_direction(breakdown)

    roadmap = build_roadmap(breakdown, priorities, primary_role)
    roadmap_summary = get_roadmap_summary(roadmap)

    history = get_analysis_history()
    patterns = detect_patterns(history)
    pattern_summary = get_pattern_summary(history)

    comparison = compare_analyses(history[0], history[1]) if len(history) >= 2 else None
    traj_scores = [h.get("overall_score", 0) for h in reversed(history) if isinstance(h, dict)]

    # =========================================================
    # SHARED
    # =========================================================

    def sec_title(kicker, title, blurb=None):
        col = [section_header(kicker, CYAN),
               text(title, 30, TEXT_PRIMARY, ft.FontWeight.BOLD)]
        if blurb:
            col.append(text(blurb, 13, TEXT_SECONDARY))
        return ft.Column(spacing=8, controls=col)

    def disclaimer(msg):
        return ft.Container(
            padding=14, border_radius=RADIUS_MD, bgcolor=BG_SURFACE,
            border=ft.Border.all(1, BORDER),
            content=ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                text("◈", 13, CYAN, ft.FontWeight.BOLD),
                ft.Container(expand=True, content=text(msg, 12, TEXT_MUTED)),
            ]),
        )

    def graph_panel(kicker, height=150, accent=CYAN):
        g = build_evidence_graph(traj_scores[-10:], width=600, height=height, accent=accent)
        gp = (g.data or {}).get("pulse") if g.data else None
        if gp:
            page.run_task(gp)
        return panel(ft.Column(spacing=12, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                mono(kicker, 9, TEXT_MUTED),
                mono(f"{len(traj_scores)} analyses", 9, TEXT_DIM),
            ]),
            wide_scroll(g),
        ]), padding=22)

    # ---- 1. OVERALL SIGNAL --------------------------------

    def build_overall():
        conf_num = ft.Text("0%", size=44, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD)
        score_num = ft.Text("0%", size=44, color=CYAN_LIGHT, weight=ft.FontWeight.BOLD)

        async def countup():
            await asyncio.sleep(0.12)
            for s in range(0, 21):
                f = s / 20.0
                conf_num.value = f"{round(confidence * f)}%"
                score_num.value = f"{round(overall_score * f)}%"
                try:
                    conf_num.update()
                    score_num.update()
                except Exception:
                    return
                await asyncio.sleep(0.022)

        page.run_task(countup)

        left = ft.Container(expand=3, content=ft.Column(spacing=18, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                section_header("Primary signal", CYAN),
                chip(f"{confidence}% confidence", CYAN),
            ]),
            ft.Text(signal, size=38, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            hairline(),
            text(reason, 15, TEXT_BODY),
            disclaimer("This is an evidence-based inference from your resume and the "
                       "target job description — not a recruiter's decision."),
        ]))

        right = ft.Container(
            expand=2, padding=24, border_radius=RADIUS_LG, bgcolor=BG_SURFACE,
            border=ft.Border.all(1, BORDER_CARD),
            content=ft.Column(spacing=20, controls=[
                ft.Column(spacing=6, controls=[
                    mono("Confidence", 9, TEXT_MUTED), conf_num, bar(confidence, CYAN, 300),
                ]),
                ft.Column(spacing=6, controls=[
                    mono("Overall evidence alignment", 9, TEXT_MUTED), score_num,
                    bar(overall_score, CYAN_LIGHT, 300),
                    text("Resume ↔ job requirements", 11, TEXT_DIM),
                ]),
            ]),
        )

        children = [
            sec_title("Section 01", "Overall signal"),
            ft.Row(spacing=24, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[left, right]),
        ]
        if len(traj_scores) >= 3:
            children.append(graph_panel("Evidence trajectory"))
        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=children)

    # ---- 2. EVIDENCE STRENGTH ----------------------------

    def build_evidence():
        strip = ft.Row(spacing=30, wrap=True, controls=[
            metric("Signals", evidence_summary["total"], accent=TEXT_PRIMARY, value_size=26),
            metric("Strong", evidence_summary["strong"], accent=SUCCESS, value_size=26),
            metric("Moderate", evidence_summary["moderate"], accent=CYAN, value_size=26),
            metric("Missing", evidence_summary["missing"], accent=ERROR, value_size=26),
        ])

        rows = []
        for item in (evidence_results[:12] if evidence_results else []):
            kw = item.get("keyword", "Unknown")
            sc = item.get("score", 0)
            st = item.get("strength", "Missing")
            rs = item.get("reason", "")
            col = strength_color(st)
            rows.append(ft.Container(
                padding=ft.Padding(left=0, top=13, right=0, bottom=13),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(width=170, content=ft.Column(spacing=3, controls=[
                        text(kw, 14, TEXT_PRIMARY, ft.FontWeight.BOLD),
                        text(st.upper(), 10.5, col, ft.FontWeight.BOLD, letter_spacing=1.2),
                    ])),
                    ft.Container(width=230, content=bar(sc, col, 210)),
                    ft.Container(width=46, content=text(f"{sc}%", 13, col, ft.FontWeight.BOLD)),
                    ft.Container(expand=True, content=text(rs, 11, TEXT_MUTED)),
                ]),
            ))
        if not rows:
            rows = [text("No evidence signals were available for this analysis.", 13, TEXT_MUTED)]

        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
            sec_title("Section 02", "Evidence strength",
                      "How strongly your resume demonstrates each detected requirement."),
            panel(strip, padding=22),
            panel(ft.Column(spacing=0, controls=[
                ft.Row(controls=[
                    ft.Container(width=170, content=mono("Requirement", 9, TEXT_DIM)),
                    ft.Container(width=230, content=mono("Demonstrated", 9, TEXT_DIM)),
                    ft.Container(width=46, content=mono("Score", 9, TEXT_DIM)),
                    ft.Container(expand=True, content=mono("Note", 9, TEXT_DIM)),
                ]),
                *rows,
            ])),
        ])

    # ---- 3. PRIORITY ENGINE -----------------------------

    def build_priority():
        rows = []
        for idx, item in enumerate(priorities, start=1):
            p = item["priority"]
            col = priority_color(p)
            rows.append(ft.Container(
                padding=18, border_radius=RADIUS_MD, bgcolor=BG_SURFACE,
                border=ft.Border.all(1, BORDER),
                content=ft.Row(spacing=18, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(width=40, height=40, border_radius=10, bgcolor=BG_ELEVATED,
                                 border=ft.Border.all(1, col), alignment=ft.Alignment(0, 0),
                                 content=text(str(idx), 15, col, ft.FontWeight.BOLD)),
                    ft.Column(spacing=5, expand=True, controls=[
                        ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                            text(item["category"], 15, TEXT_PRIMARY, ft.FontWeight.BOLD),
                            ft.Container(padding=ft.Padding(left=8, top=3, right=8, bottom=3),
                                         border_radius=10, border=ft.Border.all(1, col),
                                         content=text(p, 10, col, ft.FontWeight.BOLD, letter_spacing=1.0)),
                        ]),
                        text(item["action"], 12, TEXT_MUTED),
                    ]),
                    ft.Column(horizontal_alignment=ft.CrossAxisAlignment.END, spacing=2, controls=[
                        text(f"{item['score']}%", 17, TEXT_PRIMARY, ft.FontWeight.BOLD),
                        text(f"{item['gap']}% gap", 10, TEXT_MUTED),
                    ]),
                ]),
            ))
        if not rows:
            rows = [ft.Container(padding=18, border_radius=RADIUS_MD, bgcolor=BG_SURFACE,
                                 border=ft.Border.all(1, BORDER),
                                 content=text("No major evidence gaps were detected.", 13, SUCCESS))]

        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
            sec_title("Section 03", "Priority engine",
                      "Ranked by where closing the gap will matter most."),
            ft.Column(spacing=12, controls=rows),
        ])

    # ---- 4. ROLE DIRECTION -----------------------------

    def build_role():
        alt_rows = []
        for item in role_directions[1:5]:
            alt_rows.append(ft.Container(
                padding=ft.Padding(left=0, top=12, right=0, bottom=12),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(width=190, content=text(item["role"], 13, TEXT_BODY)),
                    ft.Container(width=210, content=bar(item["score"], PURPLE_MUTED, 200)),
                    ft.Container(expand=True, alignment=ft.Alignment(1, 0),
                                content=text(f"{item['score']}%", 12, TEXT_MUTED)),
                ]),
            ))
        if not alt_rows:
            alt_rows = [text("No additional role direction detected yet.", 12, TEXT_MUTED)]

        primary_card = ft.Container(
            expand=2, padding=26, border_radius=RADIUS_LG, bgcolor=BG_SURFACE,
            border=ft.Border.all(1, BORDER_ACCENT),
            content=ft.Column(spacing=10, controls=[
                mono("Primary direction", 9, TEXT_MUTED),
                ft.Text(primary_role["role"], size=26, color=CYAN_LIGHT, weight=ft.FontWeight.BOLD),
                text(primary_role["description"], 13, TEXT_SECONDARY),
                ft.Container(height=6),
                mono("Evidence alignment", 9, TEXT_MUTED),
                ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12, controls=[
                    bar(primary_role["score"], CYAN_LIGHT, 260),
                    text(f"{primary_role['score']}%", 14, CYAN_LIGHT, ft.FontWeight.BOLD),
                ]),
            ]),
        )

        alt_card = ft.Container(
            expand=3, padding=26, border_radius=RADIUS_LG, bgcolor=BG_CARD,
            border=ft.Border.all(1, BORDER_CARD),
            content=ft.Column(spacing=4, controls=[
                mono("Also consider", 9, TEXT_MUTED), ft.Container(height=6), *alt_rows,
            ]),
        )

        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
            sec_title("Section 04", "Role direction",
                      "Where your current evidence points — a direction signal, not a prediction."),
            ft.Row(spacing=24, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[primary_card, alt_card]),
        ])

    # ---- 5. PERSONAL ROADMAP --------------------------

    def build_roadmap_view():
        nodes = []
        for i, item in enumerate(roadmap):
            is_last = i == len(roadmap) - 1
            nodes.append(ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.START, spacing=18, controls=[
                    ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, controls=[
                        ft.Container(width=34, height=34, border_radius=17, bgcolor=PURPLE_GLOW,
                                     border=ft.Border.all(1, PURPLE_DIM), alignment=ft.Alignment(0, 0),
                                     content=text(str(item["step"]), 13, PURPLE_LIGHT, ft.FontWeight.BOLD)),
                        ft.Container(width=1, height=(0 if is_last else 46), bgcolor=PURPLE_DIM),
                    ]),
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(left=0, top=4, right=0, bottom=(0 if is_last else 22)),
                        content=ft.Column(spacing=5, controls=[
                            ft.Row(spacing=10, controls=[
                                text(item["title"], 15, TEXT_PRIMARY, ft.FontWeight.BOLD),
                                ft.Container(padding=ft.Padding(left=7, top=2, right=7, bottom=2),
                                             border_radius=8, border=ft.Border.all(1, PURPLE_DIM),
                                             content=text(item["type"].upper(), 9.5, PURPLE_LIGHT,
                                                          ft.FontWeight.BOLD, letter_spacing=1.0)),
                            ]),
                            text(item["action"], 12, TEXT_MUTED),
                        ]),
                    ),
                ],
            ))

        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
            sec_title("Section 05", "Personal roadmap", roadmap_summary),
            panel(ft.Column(spacing=0, controls=nodes), padding=26),
        ])

    # ---- 6. APPLICATION COMPARISON -------------------

    def build_comparison():
        if not comparison:
            return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
                sec_title("Section 06", "Application comparison"),
                panel(ft.Column(spacing=10, controls=[
                    text("One analysis on record.", 18, TEXT_PRIMARY, ft.FontWeight.BOLD),
                    text("Run at least one more analysis to compare score, confidence and "
                         "category movement across applications.", 13, TEXT_MUTED),
                ]), padding=26),
            ])

        sc = comparison.get("score_change", 0)
        cc = comparison.get("confidence_change", 0)
        cur = comparison.get("current_score", 0)
        prev = comparison.get("previous_score", 0)

        columns = ft.Row(spacing=0, controls=[
            ft.Container(expand=1, content=ft.Column(spacing=4, controls=[
                mono("Previous", 9, TEXT_MUTED),
                ft.Text(f"{prev}%", size=32, color=TEXT_SECONDARY, weight=ft.FontWeight.BOLD),
            ])),
            ft.Container(width=1, height=64, bgcolor=BORDER),
            ft.Container(expand=1, alignment=ft.Alignment(0, 0), content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6,
                controls=[mono("Change", 9, TEXT_MUTED), delta_badge(sc, "pts", 18)])),
            ft.Container(width=1, height=64, bgcolor=BORDER),
            ft.Container(expand=1, alignment=ft.Alignment(1, 0), content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.END, spacing=4,
                controls=[mono("Current", 9, TEXT_MUTED),
                          ft.Text(f"{cur}%", size=32, color=CYAN_LIGHT, weight=ft.FontWeight.BOLD)])),
        ])

        cat_rows = []
        for item in comparison.get("category_changes", [])[:8]:
            ch = item.get("change", 0)
            cat_rows.append(ft.Container(
                padding=ft.Padding(left=0, top=11, right=0, bottom=11),
                border=ft.Border(bottom=ft.BorderSide(1, BORDER)),
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.Container(expand=True, content=text(str(item.get("category", "")), 13, TEXT_BODY)),
                    ft.Container(width=52, alignment=ft.Alignment(1, 0),
                                content=text(f"{round(item.get('previous', 0))}%", 12, TEXT_MUTED)),
                    ft.Container(width=44, alignment=ft.Alignment(0, 0), content=delta_badge(ch, "", 12)),
                    ft.Container(width=52, alignment=ft.Alignment(1, 0),
                                content=text(f"{round(item.get('current', 0))}%", 12, TEXT_PRIMARY, ft.FontWeight.BOLD)),
                ]),
            ))
        if not cat_rows:
            cat_rows = [text("No category changes detected.", 12, TEXT_MUTED)]

        children = [
            sec_title("Section 06", "Application comparison",
                      "Latest analysis measured against the one before it."),
            panel(columns, padding=24),
        ]
        if len(traj_scores) >= 3:
            children.append(graph_panel("Score trajectory", height=140, accent=CYAN_LIGHT))
        children += [
            ft.Row(spacing=24, controls=[
                ft.Container(expand=1, content=panel(ft.Column(spacing=6, controls=[
                    mono("Confidence change", 9, TEXT_MUTED), delta_badge(cc, "pts", 15),
                ]), padding=20)),
                ft.Container(expand=1, content=panel(ft.Column(spacing=6, controls=[
                    mono("Current signal", 9, TEXT_MUTED),
                    text(str(comparison.get("current_signal", "Role Alignment")), 15,
                         TEXT_PRIMARY, ft.FontWeight.BOLD),
                ]), padding=20)),
            ]),
            panel(ft.Column(spacing=0, controls=[
                mono("What changed", 9, CYAN), ft.Container(height=4), *cat_rows,
            ])),
        ]
        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=children)

    # ---- 7. PATTERNS ---------------------------------

    def build_patterns():
        if patterns.get("total_analyses", 0) < 2:
            return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
                sec_title("Section 07", "Patterns"),
                panel(ft.Column(spacing=10, controls=[
                    text("Not enough history yet.", 18, TEXT_PRIMARY, ft.FontWeight.BOLD),
                    text("Patterns emerge once you have two or more analyses on record.", 13, TEXT_MUTED),
                ]), padding=26),
            ])

        def freq_list(items, fmt):
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

        gaps = freq_list(patterns.get("recurring_gaps", []),
                         lambda it: f"{it.get('count', 0)}/{it.get('total', 0)}")
        weak = freq_list(patterns.get("weak_categories", []),
                         lambda it: f"avg {it.get('average', 0)}%")
        sigs = freq_list(patterns.get("recurring_signals", []),
                         lambda it: f"{it.get('count', 0)}x")

        return ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
            sec_title("Section 07", "Patterns", pattern_summary),
            ft.Row(spacing=24, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Container(expand=1, content=panel(ft.Column(spacing=0, controls=[
                    mono("Recurring gaps", 9, CYAN), ft.Container(height=4), *gaps]))),
                ft.Container(expand=1, content=panel(ft.Column(spacing=0, controls=[
                    mono("Weak categories", 9, CYAN), ft.Container(height=4), *weak]))),
            ]),
            panel(ft.Column(spacing=0, controls=[
                mono("Recurring signals", 9, CYAN), ft.Container(height=4), *sigs])),
        ])

    SECTIONS = [
        ("01", "Overall signal", build_overall),
        ("02", "Evidence strength", build_evidence),
        ("03", "Priority engine", build_priority),
        ("04", "Role direction", build_role),
        ("05", "Personal roadmap", build_roadmap_view),
        ("06", "Comparison", build_comparison),
        ("07", "Patterns", build_patterns),
    ]

    # =========================================================
    # SHELL
    # =========================================================

    state = {"active": -1}

    content_host = ft.Container(
        expand=True, opacity=0,
        animate_opacity=ft.Animation(ANIM_NORMAL, ft.AnimationCurve.EASE_OUT),
        offset=ft.Offset(0.02, 0),
        animate_offset=ft.Animation(ANIM_NORMAL, ft.AnimationCurve.EASE_OUT_CUBIC),
    )

    rail_items = []

    async def _run_bar_anims():
        await asyncio.sleep(0.3)
        pending = list(animated_bars)
        animated_bars.clear()
        for fill, w, r in pending:
            try:
                fill.width = max(2.0, w * r)
                fill.update()
            except Exception:
                pass
            await asyncio.sleep(0.03)

    def render_section(i):
        if state["active"] == i:
            return
        state["active"] = i
        for j, ri in enumerate(rail_items):
            active = j == i
            ri.bgcolor = BG_SURFACE if active else TRANSPARENT
            ri.border = ft.Border(left=ft.BorderSide(2, CYAN if active else TRANSPARENT))
            ri.content.controls[0].color = CYAN_LIGHT if active else TEXT_DIM
            ri.content.controls[1].color = TEXT_PRIMARY if active else TEXT_SECONDARY
            ri.update()

        content_host.opacity = 0
        content_host.offset = ft.Offset(0.02, 0)
        content_host.update()

        async def swap():
            try:
                await asyncio.sleep(0.12)
                animated_bars.clear()
                content_host.content = SECTIONS[i][2]()
                content_host.opacity = 1
                content_host.offset = ft.Offset(0, 0)
                content_host.update()
                page.run_task(_run_bar_anims)
            except Exception:
                return

        page.run_task(swap)

    for idx, (num, label, _) in enumerate(SECTIONS):
        item = ft.Container(
            padding=ft.Padding(left=16, top=12, right=14, bottom=12),
            border_radius=RADIUS_SM,
            bgcolor=TRANSPARENT,
            border=ft.Border(left=ft.BorderSide(2, TRANSPARENT)),
            animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
            on_click=lambda e, i=idx: render_section(i),
            content=ft.Row(spacing=12, controls=[
                ft.Text(num, size=11, color=TEXT_DIM, weight=ft.FontWeight.BOLD, font_family="Courier New"),
                ft.Text(label, size=13.5, color=TEXT_SECONDARY, weight=ft.FontWeight.W_500),
            ]),
        )

        def mk(c=item, i=idx):
            def _h(e):
                if state["active"] != i:
                    c.bgcolor = BG_ELEVATED if e.data == "true" else TRANSPARENT
                    c.update()
            return _h

        item.on_hover = mk()
        rail_items.append(item)

    def new_analysis(e=None):
        if on_new_analysis:
            on_new_analysis(e)

    def go_home(e=None):
        if on_home:
            on_home(e)
        elif on_new_analysis:
            on_new_analysis(e)

    rail = ft.Container(
        width=248,
        padding=ft.Padding(left=0, top=4, right=16, bottom=4),
        border=ft.Border(right=ft.BorderSide(1, BORDER)),
        content=ft.Column(spacing=6, controls=[
            section_header("Intelligence report", CYAN),
            ft.Container(height=2),
            ft.Text(signal, size=17, color=TEXT_PRIMARY, weight=ft.FontWeight.BOLD),
            ft.Row(spacing=8, wrap=True, controls=[
                chip(f"{confidence}% conf", CYAN),
                chip(f"{overall_score}% align", TEXT_MUTED),
            ]),
            ft.Container(height=14),
            *rail_items,
            ft.Container(height=18),
            hairline(),
            ft.Container(height=12),
            ghost_button("New analysis", new_analysis),
        ]),
    )

    navbar = create_navbar(on_get_started=new_analysis, page=page,
                           is_landing=False, on_home_click=go_home)

    header = ft.Container(
        opacity=0, offset=ft.Offset(0, 0.05),
        animate_opacity=ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_offset=ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC),
        content=ft.Column(spacing=8, controls=[
            section_header("Analysis complete", CYAN),
            text("A signal has emerged.", 32, TEXT_PRIMARY, ft.FontWeight.BOLD),
            text("Move through the report section by section.", 13, TEXT_MUTED),
        ]),
    )

    body = ft.Container(
        expand=True,
        padding=ft.Padding(left=PAGE_PAD, top=24, right=PAGE_PAD, bottom=20),
        content=ft.Column(spacing=22, expand=True, controls=[
            header,
            ft.Row(spacing=28, expand=True, vertical_alignment=ft.CrossAxisAlignment.START,
                   controls=[rail, content_host]),
        ]),
    )

    page.controls.clear()
    page.add(ft.Stack(expand=True, controls=[
        animated_grid_background(page),
        ft.Column(expand=True, spacing=0, controls=[navbar, body]),
    ]))
    page.update()

    async def reveal():
        try:
            await asyncio.sleep(0.1)
            header.opacity = 1
            header.offset = ft.Offset(0, 0)
            header.update()
            await asyncio.sleep(0.14)
            render_section(0)
        except Exception:
            return

    page.run_task(reveal)
