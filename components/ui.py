import flet as ft
import flet.canvas as cv

# =============================================================
# REFRACT DESIGN SYSTEM
# Editorial intelligence — near-black canvas, off-white type,
# muted grey text. CYAN is the primary accent, VIOLET secondary.
# =============================================================

# --- SURFACES ---
BG = "#08090C"
BG_CARD = "#0C0D12"
BG_SURFACE = "#101117"
BG_ELEVATED = "#15161D"
BG_INPUT = "#0E0F15"

# --- CYAN ACCENT (primary) ---
CYAN = "#54CFE0"
CYAN_LIGHT = "#93E4EF"
CYAN_MUTED = "#2E9FB2"
CYAN_DIM = "#194A54"
CYAN_GLOW = "#0A2C34"
CYAN_DARK = "#1C8598"

# --- VIOLET ACCENT (secondary) ---
PURPLE = "#A97DF2"
PURPLE_LIGHT = "#C6ABFF"
PURPLE_MUTED = "#8257C9"
PURPLE_DIM = "#4A3A6B"
PURPLE_GLOW = "#181128"
PURPLE_DARK = "#7C4BD0"

VIOLET = PURPLE
VIOLET_LIGHT = PURPLE_LIGHT

# Primary-accent aliases (semantic — prefer these going forward)
ACCENT = CYAN
ACCENT_LIGHT = CYAN_LIGHT
ACCENT_GLOW = CYAN_GLOW

# Editorial serif stack for display headings
SERIF = "Georgia"

# --- TYPOGRAPHY ---
TEXT_PRIMARY = "#F3F1F7"
TEXT_HEADING = "#E9E7F0"
TEXT_BODY = "#C6C3D0"
TEXT_SECONDARY = "#918B9D"
TEXT_MUTED = "#6C6676"
TEXT_DIM = "#4E4956"
TEXT_FAINT = "#332F3A"

# --- BORDERS (thin) ---
BORDER = "#181920"
BORDER_CARD = "#22232C"
BORDER_ACCENT = "#245A65"     # cyan-tinted (primary accent border)
BORDER_CYAN = "#245A65"
BORDER_PURPLE = "#553C86"     # violet (secondary accent border)

# --- STATUS ---
SUCCESS = "#6FE0A8"
ERROR = "#F0808F"
WARN = "#F0C070"

# --- ANIMATION TIMINGS (ms) ---
ANIM_FAST = 220
ANIM_NORMAL = 400
ANIM_SLOW = 620
ANIM_REVEAL = 720

# --- RADIUS / SPACING ---
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16
RADIUS_XL = 20

PAGE_PAD = 48
SECTION_GAP = 26


# =============================================================
# TEXT HELPER
# =============================================================

def text(value, size=14, color=TEXT_PRIMARY, weight=None, font_family=None,
         letter_spacing=None, italic=None):
    kwargs = {
        "value": value,
        "size": size,
        "color": color,
        "weight": weight,
    }
    if font_family:
        kwargs["font_family"] = font_family
    if italic is not None:
        kwargs["italic"] = italic
    if letter_spacing is not None:
        kwargs["style"] = ft.TextStyle(letter_spacing=letter_spacing)
    return ft.Text(**kwargs)


# =============================================================
# MONO LABEL — small editorial eyebrow
# =============================================================

def mono(value, size=12, color=TEXT_MUTED, weight=ft.FontWeight.BOLD, spacing=1.8):
    # Card/topic labels — floored so nothing renders uncomfortably small,
    # while keeping relative hierarchy across call sites.
    size = max(float(size) + 1.5, 11.0)
    return ft.Text(
        str(value).upper(),
        size=size,
        color=color,
        weight=weight,
        font_family="Courier New",
        style=ft.TextStyle(letter_spacing=spacing),
    )


def section_header(label, color=CYAN):
    return mono(label, size=12.5, color=color, spacing=2.2)


# =============================================================
# TOAST — Flet 0.86.5-safe transient message
# (page.snack_bar was removed; SnackBar is now a DialogControl)
# =============================================================

def toast(page, message, error=False):
    if page is None:
        return
    sb = ft.SnackBar(
        content=ft.Row(spacing=10, controls=[
            ft.Text("!" if error else "◈", size=13,
                    color=("#FFFFFF" if error else PURPLE), weight=ft.FontWeight.BOLD),
            ft.Text(str(message), size=13,
                    color=("#FFFFFF" if error else TEXT_PRIMARY), weight=ft.FontWeight.W_500),
        ]),
        bgcolor=("#C24A57" if error else BG_ELEVATED),
        behavior=ft.SnackBarBehavior.FIXED,
        padding=ft.Padding(left=22, top=16, right=22, bottom=16),
        duration=3500,
    )
    try:
        page.show_dialog(sb)
    except Exception:
        try:
            page.overlay.append(sb)
            sb.open = True
            page.update()
        except Exception:
            pass


# =============================================================
# HAIRLINE
# =============================================================

def hairline(vertical=False, color=BORDER, length=None):
    if vertical:
        return ft.Container(width=1, height=length, bgcolor=color)
    return ft.Container(height=1, width=length, bgcolor=color)


# =============================================================
# CHIP / PILL
# =============================================================

def chip(label, color=CYAN, filled=False):
    return ft.Container(
        padding=ft.Padding(left=11, top=6, right=11, bottom=6),
        border_radius=20,
        bgcolor=(CYAN_GLOW if filled else "transparent"),
        border=ft.Border.all(1, color if not filled else "transparent"),
        content=ft.Text(
            str(label).upper(),
            size=10.5,
            color=color,
            weight=ft.FontWeight.BOLD,
            font_family="Courier New",
            style=ft.TextStyle(letter_spacing=1.3),
        ),
    )


# =============================================================
# DELTA BADGE — signed change indicator
# =============================================================

def delta_badge(value, unit="pts", size=13):
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = 0.0

    if v > 0:
        sym, col = "▲", SUCCESS
    elif v < 0:
        sym, col = "▼", ERROR
    else:
        sym, col = "•", TEXT_MUTED

    return ft.Row(
        tight=True,
        spacing=5,
        controls=[
            ft.Text(sym, size=size - 3, color=col),
            ft.Text(
                f"{abs(round(v))} {unit}".strip(),
                size=size,
                color=col,
                weight=ft.FontWeight.BOLD,
            ),
        ],
    )


# =============================================================
# METRIC CELL — for horizontal metric strips
# =============================================================

def metric(label, value, sub=None, accent=TEXT_PRIMARY, value_size=30):
    controls = [mono(label, size=9, color=TEXT_MUTED, spacing=1.8)]
    if value != "" and value is not None:
        controls.append(
            ft.Text(str(value), size=value_size, color=accent, weight=ft.FontWeight.BOLD))
    if sub is not None:
        if isinstance(sub, str):
            controls.append(ft.Text(sub, size=11, color=TEXT_SECONDARY))
        else:
            controls.append(sub)
    return ft.Column(spacing=6, controls=controls)


# =============================================================
# PANEL — minimal card, thin border, generous padding
# =============================================================

def panel(content, padding=26, accent=False, bg=BG_CARD, radius=RADIUS_LG,
          border_color=None):
    return ft.Container(
        padding=padding,
        border_radius=radius,
        bgcolor=bg,
        border=ft.Border.all(1, border_color or (BORDER_ACCENT if accent else BORDER_CARD)),
        content=content,
    )


# =============================================================
# PRIMARY BUTTON — cyan CTA with a soft cyan/violet glow
# =============================================================

def _glow(blur, cyan_op, offset_y, spread=0):
    return ft.BoxShadow(
        spread_radius=spread, blur_radius=blur,
        color=ft.Colors.with_opacity(cyan_op, CYAN), offset=ft.Offset(0, offset_y),
    )


def primary_button(label, on_click=None, icon="→", width=None):
    row = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True,
        spacing=10,
        controls=[
            ft.Text(label, size=14, color="#04161A", weight=ft.FontWeight.BOLD),
            ft.Text(icon, size=15, color="#04161A", weight=ft.FontWeight.BOLD),
        ],
    )

    btn = ft.Container(
        width=width,
        height=46,
        padding=ft.Padding(left=24, top=0, right=24, bottom=0),
        border_radius=RADIUS_MD,
        bgcolor=CYAN,
        border=ft.Border.all(1, CYAN_LIGHT),
        alignment=ft.Alignment(0, 0),
        shadow=_glow(24, 0.22, 6),
        animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        content=row,
        on_click=on_click,
    )

    def _hover(e):
        hovering = e.data == "true"
        btn.bgcolor = CYAN_LIGHT if hovering else CYAN
        btn.scale = 1.02 if hovering else 1.0
        btn.shadow = _glow(40, 0.40, 9, spread=1) if hovering else _glow(24, 0.22, 6)
        btn.update()

    btn.on_hover = _hover
    return btn


def ghost_button(label, on_click=None, icon="→", accent=CYAN):
    btn = ft.Container(
        padding=ft.Padding(left=18, top=11, right=18, bottom=11),
        border_radius=RADIUS_MD,
        border=ft.Border.all(1, BORDER_ACCENT),
        bgcolor="transparent",
        shadow=_glow(14, 0.0, 4),
        animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        content=ft.Row(
            tight=True, spacing=9,
            controls=[
                ft.Text(label, size=13, color=accent, weight=ft.FontWeight.BOLD),
                ft.Text(icon, size=13, color=accent, weight=ft.FontWeight.BOLD),
            ],
        ),
        on_click=on_click,
    )

    def _h(e):
        hovering = e.data == "true"
        btn.bgcolor = CYAN_GLOW if hovering else "transparent"
        btn.border = ft.Border.all(1, CYAN_MUTED if hovering else BORDER_ACCENT)
        btn.shadow = _glow(22, 0.18, 5) if hovering else _glow(14, 0.0, 4)
        btn.update()

    btn.on_hover = _h
    return btn


# =============================================================
# BACKGROUND — faint drifting grid + soft cyan / violet glows
# =============================================================

_GRID_LINE = "#1B2230"
_SPACING = 112


def _grid_layer(cols=28, rows=22, offx=-140, offy=-120):
    lines = []
    for i in range(cols):
        lines.append(ft.Container(left=offx + i * _SPACING, top=offy,
                                  width=1, height=(rows + 4) * _SPACING,
                                  bgcolor=_GRID_LINE, opacity=0.7))
    for j in range(rows):
        lines.append(ft.Container(left=offx, top=offy + j * _SPACING,
                                  width=(cols + 4) * _SPACING, height=1,
                                  bgcolor=_GRID_LINE, opacity=0.7))
    return ft.Stack(controls=lines, width=(cols + 4) * _SPACING,
                    height=(rows + 4) * _SPACING)


def grid_background():
    return ft.Stack(expand=True, controls=[
        ft.Container(content=_grid_layer(), left=0, top=0),
    ])


def ambient_background():
    return animated_grid_background(None)


def animated_grid_background(page=None):
    """Full-bleed drifting grid + ambient glows.

    Returns a Stack. If a `page` is given the slow drift starts immediately;
    otherwise schedule `stack.data['anim']` with `page.run_task` after mount.
    """
    grid = ft.Container(
        content=_grid_layer(),
        left=-140, top=-120,
        animate_offset=ft.Animation(9000, ft.AnimationCurve.EASE_IN_OUT),
        offset=ft.Offset(0, 0),
    )

    glow_cyan = ft.Container(
        width=560, height=560, border_radius=280, left=-210, top=-40,
        bgcolor="#0B2E36", opacity=0.5,
        animate_offset=ft.Animation(14000, ft.AnimationCurve.EASE_IN_OUT),
        offset=ft.Offset(0, 0),
    )
    glow_violet = ft.Container(
        width=520, height=520, border_radius=260, right=-200, top=220,
        bgcolor="#161033", opacity=0.55,
        animate_offset=ft.Animation(16000, ft.AnimationCurve.EASE_IN_OUT),
        offset=ft.Offset(0, 0),
    )

    stack = ft.Stack(expand=True, controls=[grid, glow_cyan, glow_violet])

    async def drift():
        import asyncio
        await asyncio.sleep(0.6)  # let the page mount first
        step = 0
        while True:
            step += 1
            if step % 2:
                grid.offset = ft.Offset(0.012, 0.016)
                glow_cyan.offset = ft.Offset(0.03, 0.02)
                glow_violet.offset = ft.Offset(-0.025, -0.02)
            else:
                grid.offset = ft.Offset(-0.01, -0.012)
                glow_cyan.offset = ft.Offset(-0.02, -0.015)
                glow_violet.offset = ft.Offset(0.02, 0.02)
            try:
                stack.update()
            except Exception:
                return
            await asyncio.sleep(9)

    stack.data = {"anim": drift}

    if page is not None:
        try:
            page.run_task(drift)
        except Exception:
            pass

    return stack


# =============================================================
# LOGO
# =============================================================

def _prism_mark(size=32):
    """A small 'refraction' emblem — a prism splitting an incoming ray."""
    s = size

    def sc(x, y):
        return x / 32 * s, y / 32 * s

    def line(a, b, color, w=1.6):
        x1, y1 = sc(*a)
        x2, y2 = sc(*b)
        return cv.Line(x1, y1, x2, y2, paint=ft.Paint(
            color=color, stroke_width=w, stroke_cap=ft.StrokeCap.ROUND))

    tri = cv.Path(
        [
            cv.Path.MoveTo(*sc(16, 6)),
            cv.Path.LineTo(*sc(7, 25)),
            cv.Path.LineTo(*sc(25, 25)),
            cv.Path.Close(),
        ],
        paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1.7,
                       color=CYAN, stroke_join=ft.StrokeJoin.ROUND),
    )
    tri_fill = cv.Path(
        [
            cv.Path.MoveTo(*sc(16, 6)),
            cv.Path.LineTo(*sc(7, 25)),
            cv.Path.LineTo(*sc(25, 25)),
            cv.Path.Close(),
        ],
        paint=ft.Paint(style=ft.PaintingStyle.FILL,
                       color=ft.Colors.with_opacity(0.10, CYAN)),
    )

    shapes = [
        tri_fill, tri,
        line((1, 17), (12, 17), ft.Colors.with_opacity(0.85, "#F4F2F7"), 1.6),
        line((18, 19), (31, 12), CYAN_LIGHT, 1.5),
        line((18, 20), (31, 20), CYAN, 1.5),
        line((18, 21), (31, 28), PURPLE_LIGHT, 1.5),
    ]
    return cv.Canvas(shapes=shapes, width=s, height=s)


def create_logo(font_size=18, on_click=None):
    emblem = ft.Container(
        width=34, height=34, border_radius=9,
        gradient=ft.LinearGradient(
            colors=["#0A2A32", "#140E26"],
            begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
        ),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.55, CYAN_MUTED)),
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=14,
            color=ft.Colors.with_opacity(0.20, CYAN), offset=ft.Offset(0, 3),
        ),
        content=_prism_mark(22),
    )

    brand = ft.Row(tight=True, spacing=0, controls=[
        ft.Text("REFRACT", size=font_size, color=TEXT_PRIMARY,
                weight=ft.FontWeight.BOLD, font_family=SERIF,
                style=ft.TextStyle(letter_spacing=3.0)),
    ])

    content = ft.Row(spacing=12, tight=True,
                     vertical_alignment=ft.CrossAxisAlignment.CENTER,
                     controls=[emblem, brand])

    if on_click:
        box = ft.Container(
            content=content, on_click=on_click,
            padding=ft.Padding(left=4, top=4, right=8, bottom=4),
            border_radius=8,
            animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        )

        def _h(e):
            box.bgcolor = BG_ELEVATED if e.data == "true" else "transparent"
            box.update()

        box.on_hover = _h
        return box

    return content


# =============================================================
# NAVBAR
# =============================================================

def create_navbar(on_get_started=None, page=None, on_section_click=None,
                  is_landing=True, on_home_click=None):
    logo = create_logo(18, on_click=on_home_click)

    if not is_landing:
        home_btn = ft.Container(
            on_click=on_home_click or on_get_started,
            padding=ft.Padding(left=14, top=8, right=14, bottom=8),
            border_radius=8,
            border=ft.Border.all(1, BORDER_CARD),
            bgcolor=BG_CARD,
            animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
            content=ft.Row(
                tight=True, spacing=7,
                controls=[
                    text("←", 12, CYAN, ft.FontWeight.BOLD),
                    text("Home", 12, TEXT_PRIMARY, ft.FontWeight.BOLD),
                ],
            ),
        )

        def _hb(e):
            home_btn.border = ft.Border.all(
                1, BORDER_ACCENT if e.data == "true" else BORDER_CARD)
            home_btn.update()

        home_btn.on_hover = _hb

        return ft.Container(
            padding=ft.Padding(left=PAGE_PAD, top=16, right=PAGE_PAD, bottom=16),
            border=ft.Border(bottom=ft.BorderSide(width=1, color=BORDER)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[logo, home_btn],
            ),
        )

    def handle_nav(sec_name):
        if on_section_click:
            on_section_click(sec_name)
        elif page:
            toast(page, sec_name)

    nav_items_data = [
        ("Product", "product"),
        ("How it works", "how_it_works"),
        ("Insights", "insights"),
    ]

    nav_items = []
    for label, key in nav_items_data:
        item = ft.Container(
            content=text(label, 13, TEXT_SECONDARY),
            on_click=lambda e, k=key: handle_nav(k),
            padding=ft.Padding(left=10, top=6, right=10, bottom=6),
            border_radius=6,
            animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        )

        def make_hover(c=item):
            def _h(e):
                c.bgcolor = BG_ELEVATED if e.data == "true" else "transparent"
                c.content.color = TEXT_PRIMARY if e.data == "true" else TEXT_SECONDARY
                c.update()
            return _h

        item.on_hover = make_hover(item)
        nav_items.append(item)

    get_started = ft.Container(
        on_click=on_get_started,
        padding=ft.Padding(left=16, top=9, right=16, bottom=9),
        border_radius=8,
        border=ft.Border.all(1, BORDER_ACCENT),
        shadow=_glow(12, 0.0, 3),
        animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        content=text("Get started  →", 13, CYAN, ft.FontWeight.BOLD),
    )

    def _gs(e):
        hovering = e.data == "true"
        get_started.bgcolor = CYAN_GLOW if hovering else "transparent"
        get_started.border = ft.Border.all(1, CYAN_MUTED if hovering else BORDER_ACCENT)
        get_started.shadow = _glow(20, 0.16, 4) if hovering else _glow(12, 0.0, 3)
        get_started.update()

    get_started.on_hover = _gs

    return ft.Container(
        padding=ft.Padding(left=PAGE_PAD, top=16, right=PAGE_PAD, bottom=16),
        border=ft.Border(bottom=ft.BorderSide(width=1, color=BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[logo, ft.Row(spacing=14, controls=nav_items), get_started],
        ),
    )


# =============================================================
# UPLOAD CARD (kept for compatibility)
# =============================================================

def upload_card(number, title, subtitle, status, on_click=None):
    status_color = TEXT_DIM
    if status == "Required":
        status_color = PURPLE
    elif status == "Uploaded successfully":
        status_color = SUCCESS

    card = ft.Container(
        expand=True, height=200, padding=22,
        border_radius=RADIUS_LG, bgcolor=BG_CARD,
        border=ft.Border.all(1, BORDER_CARD),
        animate=ft.Animation(ANIM_FAST, ft.AnimationCurve.EASE_OUT),
        content=ft.Column(
            spacing=10,
            controls=[
                mono(number, 10, TEXT_DIM),
                text(title, 20, TEXT_HEADING, ft.FontWeight.BOLD),
                mono(subtitle, 10, TEXT_MUTED, spacing=1.2),
                ft.Container(
                    padding=ft.Padding(left=14, top=9, right=14, bottom=9),
                    border_radius=RADIUS_SM, bgcolor=BG_INPUT,
                    border=ft.Border.all(1, BORDER_PURPLE),
                    on_click=on_click,
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            text("+", 16, PURPLE, ft.FontWeight.BOLD),
                            text("Choose file", 12, TEXT_BODY),
                        ],
                    ),
                ),
                text(status, 10, status_color, ft.FontWeight.BOLD, letter_spacing=0.5),
            ],
        ),
    )

    def _h(e):
        card.border = ft.Border.all(
            1, BORDER_ACCENT if e.data == "true" else BORDER_CARD)
        card.update()

    card.on_hover = _h
    return card


# =============================================================
# ANIMATED REVEAL — staggered opacity/offset sequence
# =============================================================

async def reveal_sequence(page, items, delay=0.09, initial=0.12):
    """items: list of controls with animate_opacity set. Fades them in, staggered."""
    import asyncio
    await asyncio.sleep(initial)
    for it in items:
        try:
            it.opacity = 1
            if hasattr(it, "offset"):
                it.offset = ft.Offset(0, 0)
            it.update()
        except Exception:
            pass
        await asyncio.sleep(delay)


def mountable(control, dy=0.06):
    """Wrap intent: set a control to start hidden + slightly offset for reveal."""
    control.opacity = 0
    control.offset = ft.Offset(0, dy)
    control.animate_opacity = ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC)
    control.animate_offset = ft.Animation(ANIM_REVEAL, ft.AnimationCurve.EASE_OUT_CUBIC)
    return control
