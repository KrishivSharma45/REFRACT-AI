"""
REFRACT — Editorial evidence-trajectory graph.

A premium, stock-market-style line chart drawn with flet.canvas.
Stable on Flet 0.86.5 (no rotated Containers, no external deps).

Represents application / evidence trajectory — NOT financial data.
"""

import flet as ft
import flet.canvas as cv


# Editorial palette (kept local so this module has no hard dependency
# on the design-token module import order).
_VIOLET = "#A97DF2"
_VIOLET_SOFT = "#7C5BB8"
_GRID = "#17181F"
_GRID_STRONG = "#1E1F28"
_AREA_TOP = "#A97DF2"
_ENDPOINT = "#C9A6FF"


def _catmull_rom_to_bezier(points, tension=0.5):
    """Convert a list of (x, y) points into smooth cubic-bezier segments."""
    if len(points) < 2:
        return []

    pts = [points[0]] + list(points) + [points[-1]]
    segments = []

    for i in range(1, len(pts) - 2):
        p0 = pts[i - 1]
        p1 = pts[i]
        p2 = pts[i + 1]
        p3 = pts[i + 2]

        cp1x = p1[0] + (p2[0] - p0[0]) * tension / 3.0
        cp1y = p1[1] + (p2[1] - p0[1]) * tension / 3.0
        cp2x = p2[0] - (p3[0] - p1[0]) * tension / 3.0
        cp2y = p2[1] - (p3[1] - p1[1]) * tension / 3.0

        segments.append((cp1x, cp1y, cp2x, cp2y, p2[0], p2[1]))

    return segments


def build_evidence_graph(
    values,
    width=440,
    height=190,
    *,
    accent=_VIOLET,
    show_grid=True,
    show_area=True,
    glow_endpoint=True,
    pad_x=6,
    pad_top=18,
    pad_bottom=14,
):
    """
    Return a Stack containing the trajectory graph.

    `values` — any numeric sequence (scores, confidence, deltas...).
    The graph auto-normalises to its own vertical space.
    """

    values = [float(v) for v in (values or [])]

    if len(values) < 2:
        values = (values + [50.0, 50.0])[:2]

    lo = min(values)
    hi = max(values)
    span = (hi - lo) or 1.0

    inner_w = width - pad_x * 2
    inner_h = height - pad_top - pad_bottom
    step = inner_w / (len(values) - 1)

    points = []
    for i, v in enumerate(values):
        x = pad_x + i * step
        # invert Y (canvas origin top-left); keep a little breathing room
        norm = (v - lo) / span
        y = pad_top + (1.0 - norm) * inner_h
        points.append((x, y))

    shapes = []

    # ---- subtle grid ------------------------------------------------
    if show_grid:
        for gy in range(1, 4):
            yy = pad_top + inner_h * (gy / 4.0)
            shapes.append(
                cv.Line(
                    pad_x, yy, width - pad_x, yy,
                    paint=ft.Paint(color=_GRID, stroke_width=1),
                )
            )
        for gx in range(1, 5):
            xx = pad_x + inner_w * (gx / 5.0)
            shapes.append(
                cv.Line(
                    xx, pad_top - 6, xx, height - pad_bottom,
                    paint=ft.Paint(color=_GRID, stroke_width=1),
                )
            )
        # baseline
        shapes.append(
            cv.Line(
                pad_x, height - pad_bottom, width - pad_x, height - pad_bottom,
                paint=ft.Paint(color=_GRID_STRONG, stroke_width=1),
            )
        )

    segments = _catmull_rom_to_bezier(points, tension=0.55)

    # ---- area fill under the curve --------------------------------
    if show_area:
        area_elems = [cv.Path.MoveTo(points[0][0], points[0][1])]
        for cp1x, cp1y, cp2x, cp2y, x, y in segments:
            area_elems.append(cv.Path.CubicTo(cp1x, cp1y, cp2x, cp2y, x, y))
        area_elems.append(cv.Path.LineTo(points[-1][0], height - pad_bottom))
        area_elems.append(cv.Path.LineTo(points[0][0], height - pad_bottom))
        area_elems.append(cv.Path.Close())

        shapes.append(
            cv.Path(
                area_elems,
                paint=ft.Paint(
                    style=ft.PaintingStyle.FILL,
                    gradient=ft.PaintLinearGradient(
                        begin=(0, pad_top),
                        end=(0, height - pad_bottom),
                        colors=[
                            ft.Colors.with_opacity(0.22, _AREA_TOP),
                            ft.Colors.with_opacity(0.06, _AREA_TOP),
                            "transparent",
                        ],
                        color_stops=[0.0, 0.55, 1.0],
                    ),
                ),
            )
        )

    # ---- faint underlay line (glow) ------------------------------
    line_elems = [cv.Path.MoveTo(points[0][0], points[0][1])]
    for cp1x, cp1y, cp2x, cp2y, x, y in segments:
        line_elems.append(cv.Path.CubicTo(cp1x, cp1y, cp2x, cp2y, x, y))

    shapes.append(
        cv.Path(
            list(line_elems),
            paint=ft.Paint(
                style=ft.PaintingStyle.STROKE,
                stroke_width=6,
                color=ft.Colors.with_opacity(0.14, accent),
                stroke_cap=ft.StrokeCap.ROUND,
                stroke_join=ft.StrokeJoin.ROUND,
            ),
        )
    )

    # ---- primary line -------------------------------------------
    shapes.append(
        cv.Path(
            list(line_elems),
            paint=ft.Paint(
                style=ft.PaintingStyle.STROKE,
                stroke_width=2,
                color=accent,
                stroke_cap=ft.StrokeCap.ROUND,
                stroke_join=ft.StrokeJoin.ROUND,
            ),
        )
    )

    canvas = cv.Canvas(shapes=shapes, width=width, height=height)

    # ---- glowing / pulsing current endpoint --------------------
    end_x, end_y = points[-1]

    layers = [canvas]

    if glow_endpoint:
        halo = ft.Container(
            width=26,
            height=26,
            border_radius=13,
            bgcolor=ft.Colors.with_opacity(0.16, accent),
            left=end_x - 13,
            top=end_y - 13,
            opacity=0.0,
            scale=0.7,
            animate_opacity=ft.Animation(1400, ft.AnimationCurve.EASE_IN_OUT),
            animate_scale=ft.Animation(1400, ft.AnimationCurve.EASE_IN_OUT),
        )
        dot = ft.Container(
            width=9,
            height=9,
            border_radius=5,
            bgcolor=_ENDPOINT,
            border=ft.Border.all(2, accent),
            left=end_x - 4.5,
            top=end_y - 4.5,
        )
        layers.append(halo)
        layers.append(dot)

        async def _pulse():
            import asyncio

            await asyncio.sleep(0.4)
            grow = True
            try:
                while True:
                    halo.opacity = 0.9 if grow else 0.25
                    halo.scale = 1.25 if grow else 0.8
                    try:
                        halo.update()
                    except Exception:
                        return
                    grow = not grow
                    await asyncio.sleep(1.4)
            except Exception:
                return

        # expose the coroutine so callers can schedule it with page.run_task
        canvas.data = {"pulse": _pulse}

    stack = ft.Stack(controls=layers, width=width, height=height)
    stack.data = canvas.data
    return stack
