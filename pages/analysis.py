import asyncio
import flet as ft

from components.ui import (
    text, mono, section_header, primary_button, ghost_button, toast,
    ambient_background, animated_grid_background, grid_background, create_navbar, hairline, chip,
    BG, BG_CARD, BG_SURFACE, BG_ELEVATED, BG_INPUT,
    CYAN, CYAN_LIGHT, CYAN_MUTED, CYAN_GLOW,
    CYAN,
    TEXT_PRIMARY, TEXT_HEADING, TEXT_BODY, TEXT_SECONDARY, TEXT_MUTED, TEXT_DIM,
    BORDER, BORDER_CARD, BORDER_ACCENT, BORDER_ACCENT,
    SUCCESS, ERROR,
    ANIM_FAST, ANIM_NORMAL, ANIM_REVEAL,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, PAGE_PAD, SECTION_GAP,
)

try:
    from components.voice import create_voice_button
    _VOICE_OK = True
except Exception:  # pragma: no cover
    _VOICE_OK = False


def show_analysis(
    page: ft.Page,
    on_begin_analysis=None,
    file_picker=None,
    selected_files=None,
    on_home=None,
    on_insights=None,
):
    page.controls.clear()

    if selected_files is None:
        selected_files = {"resume": None, "jd": None, "rejection": None}

    # =========================================================
    # FILE SELECTION
    # =========================================================

    async def open_picker(file_type):
        if file_picker is None:
            toast(page, "File picker is not available.", error=True)
            return

        allowed = ["pdf", "docx"] if file_type == "resume" else ["pdf", "txt"]

        try:
            files = await file_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=allowed,
                with_data=True,
            )
            if not files:
                return

            sel = files[0]
            selected_files[file_type] = sel

            slot = SLOTS[file_type]
            slot["button"].content = ft.Row(spacing=8, controls=[
                text("✓", 15, SUCCESS),
                ft.Text(sel.name, size=12, color=TEXT_PRIMARY,
                        overflow=ft.TextOverflow.ELLIPSIS, max_lines=1, expand=True),
            ])
            slot["button"].border = ft.Border.all(1, BORDER_ACCENT)
            slot["status"].value = "Uploaded"
            slot["status"].color = SUCCESS
            slot["card"].border = ft.Border.all(1, BORDER_ACCENT)
            page.update()

        except Exception as error:
            toast(page, f"Could not select file: {error}", error=True)

    def make_button(file_type):
        b = ft.Container(
            padding=12, border_radius=RADIUS_SM, bgcolor=BG_INPUT,
            border=ft.Border.all(1, BORDER_ACCENT),
            animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
            on_click=lambda e: page.run_task(open_picker, file_type),
            content=ft.Row(spacing=8, controls=[
                text("+", 16, CYAN, ft.FontWeight.BOLD),
                text("Choose file", 12, TEXT_SECONDARY),
            ]),
        )
        return b

    SLOTS = {
        "resume": {"num": "01", "title": "Resume", "sub": "PDF / DOCX", "req": "Required"},
        "jd": {"num": "02", "title": "Job description", "sub": "PDF / TXT", "req": "Required"},
        "rejection": {"num": "03", "title": "Rejection / feedback", "sub": "PDF / TXT", "req": "Optional"},
    }

    cards = []
    for key, meta in SLOTS.items():
        btn = make_button(key)
        status = ft.Text(meta["req"], size=9, color=(CYAN if meta["req"] == "Required" else TEXT_DIM),
                         weight=ft.FontWeight.BOLD, style=ft.TextStyle(letter_spacing=1.2))
        card = ft.Container(
            expand=True, padding=22, border_radius=RADIUS_LG, bgcolor=BG_CARD,
            border=ft.Border.all(1, BORDER_CARD),
            animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
            content=ft.Column(spacing=12, controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    mono(meta["num"], 10, TEXT_DIM),
                    status,
                ]),
                text(meta["title"], 19, TEXT_HEADING, ft.FontWeight.BOLD),
                mono(meta["sub"], 9, TEXT_MUTED, spacing=1.2),
                ft.Container(height=2),
                btn,
            ]),
        )

        def hv(c=card, k=key):
            def _h(e):
                if selected_files.get(k) is not None:
                    return
                c.border = ft.Border.all(1, BORDER_ACCENT if e.data == "true" else BORDER_CARD)
                c.update()
            return _h

        card.on_hover = hv()
        SLOTS[key]["button"] = btn
        SLOTS[key]["status"] = status
        SLOTS[key]["card"] = card
        cards.append(card)

    # =========================================================
    # BEGIN
    # =========================================================

    def begin_analysis(e=None):
        if selected_files["resume"] is None:
            toast(page, "Upload your resume first.", error=True)
            return
        if selected_files["jd"] is None:
            toast(page, "Upload the job description first.", error=True)
            return
        if on_begin_analysis:
            on_begin_analysis(e)

    def go_home(e=None):
        if on_home:
            on_home(e)

    # =========================================================
    # VOICE (optional)
    # =========================================================

    def handle_voice(result):
        action = result.get("action")
        if action in ("start_analysis", "new_analysis"):
            begin_analysis()
        elif action == "open_insights" and on_insights:
            on_insights()
        elif action in ("compare", "show_roadmap", "show_patterns") and on_insights:
            on_insights()
        elif action == "go_home":
            go_home()

    voice_control = None
    if _VOICE_OK:
        try:
            voice_control = create_voice_button(page, on_command=handle_voice)
        except Exception:
            voice_control = None

    # =========================================================
    # LAYOUT
    # =========================================================

    navbar = create_navbar(on_get_started=begin_analysis, page=page,
                           is_landing=False, on_home_click=go_home)

    heading = ft.Column(spacing=8, controls=[
        section_header("New analysis", CYAN),
        text("Give us the evidence.", 40, TEXT_PRIMARY, ft.FontWeight.BOLD),
        text("We'll find the signal.", 40, CYAN_LIGHT, ft.FontWeight.BOLD),
        ft.Container(height=4),
        text("Provide your candidate documents below. REFRACT separates objective "
             "evidence from noise to highlight what deserves attention.", 14, TEXT_SECONDARY),
    ])

    guide = ft.Container(
        expand=True, padding=20, border_radius=RADIUS_MD, bgcolor=BG_CARD,
        border=ft.Border.all(1, BORDER_CARD),
        content=ft.Column(spacing=8, controls=[
            mono("Input best practices", 10, CYAN),
            text("• Include your full technical skills and experience in the resume.\n"
                 "• Upload the exact job requirements section from the posting.\n"
                 "• Optional rejection emails help isolate specific interviewer feedback.",
                 12, TEXT_MUTED),
        ]),
    )

    assurance = ft.Container(
        expand=True, padding=20, border_radius=RADIUS_MD, bgcolor=BG_CARD,
        border=ft.Border.all(1, BORDER_CARD),
        content=ft.Column(spacing=8, controls=[
            mono("Local & private processing", 10, CYAN),
            text("• Documents are parsed locally for text analysis.\n"
                 "• No resume data is shared or sold to third parties.\n"
                 "• Analysis runs inside your active application session.",
                 12, TEXT_MUTED),
        ]),
    )

    trust = ft.Container(
        padding=16, border_radius=RADIUS_MD, bgcolor=BG_SURFACE,
        border=ft.Border.all(1, BORDER),
        content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
            text("◎", 18, CYAN),
            ft.Column(spacing=3, expand=True, controls=[
                text("Evidence-first analysis", 13, TEXT_PRIMARY, ft.FontWeight.BOLD),
                text("REFRACT never presents an AI inference as a confirmed recruiter decision.",
                     11, TEXT_SECONDARY),
            ]),
        ]),
    )

    action_row_controls = []
    if voice_control is not None:
        action_row_controls.append(
            ft.Row(spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                voice_control,
                text("say “start analysis”", 11, TEXT_DIM),
            ])
        )
    action_row_controls.append(ft.Container(expand=True))
    action_row_controls.append(primary_button("Begin analysis", begin_analysis))

    main_content = ft.Container(
        opacity=0, offset=ft.Offset(0, 0.04),
        animate_opacity=ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_offset=ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC),
        content=ft.Column(spacing=SECTION_GAP, scroll=ft.ScrollMode.AUTO, controls=[
            heading,
            ft.Row(spacing=18, controls=cards),
            ft.Row(spacing=18, controls=[guide, assurance]),
            trust,
            ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=action_row_controls),
        ]),
    )

    page.add(ft.Stack(expand=True, controls=[
        animated_grid_background(page),
        ft.Column(expand=True, spacing=0, controls=[
            navbar,
            ft.Container(expand=True, padding=PAGE_PAD, content=main_content),
        ]),
    ]))
    page.update()

    async def entrance():
        try:
            await asyncio.sleep(0.12)
            main_content.opacity = 1
            main_content.offset = ft.Offset(0, 0)
            main_content.update()
        except Exception:
            return

    page.run_task(entrance)
