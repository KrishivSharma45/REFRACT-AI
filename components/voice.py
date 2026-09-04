import asyncio
import flet as ft

from services.voice import listen_once
from components.ui import (
    text,
    PURPLE_LIGHT,
    PURPLE_GLOW,
    PURPLE_DIM,
    BG_INPUT,
    BORDER_PURPLE,
    TEXT_MUTED,
    SUCCESS,
    ERROR,
    ANIM_FAST,
    ANIM_NORMAL,
)


def create_voice_button(page: ft.Page, on_command=None):
    status = text(
        "",
        size=11,
        color=TEXT_MUTED,
    )

    spinner = ft.Container(
        content=ft.ProgressRing(width=12, height=12, stroke_width=2, color=PURPLE_LIGHT),
        visible=False,
    )

    pulse_ring = ft.Container(
        width=54,
        height=54,
        border_radius=27,
        border=ft.Border.all(2, PURPLE_DIM),
        bgcolor="transparent",
        scale=1.0,
        animate_scale=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_IN_OUT),
        opacity=0.0,
    )

    button = ft.Container(
        width=48,
        height=48,
        border_radius=24,
        bgcolor=BG_INPUT,
        border=ft.Border.all(1, BORDER_PURPLE),
        alignment=ft.Alignment(0, 0),
        content=text("🎙", size=18),
        animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
    )

    status_row = ft.Row(
        controls=[spinner, status],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=6,
    )

    is_listening = False

    async def pulse_animation():
        while is_listening:
            pulse_ring.scale = 1.15
            pulse_ring.opacity = 0.5
            page.update()
            await asyncio.sleep(0.4)
            if not is_listening:
                break
            pulse_ring.scale = 1.0
            pulse_ring.opacity = 0.1
            page.update()
            await asyncio.sleep(0.4)

        pulse_ring.scale = 1.0
        pulse_ring.opacity = 0.0
        page.update()

    async def listen(e):
        nonlocal is_listening
        if is_listening:
            return

        is_listening = True
        button.disabled = True
        button.bgcolor = PURPLE_GLOW
        button.scale = 0.95

        status.value = "Listening..."
        status.color = PURPLE_LIGHT
        spinner.visible = True

        page.update()

        page.run_task(pulse_animation)

        try:
            result = await asyncio.to_thread(listen_once)

            is_listening = False  # Stop pulse

            # Processing state
            status.value = "Processing..."
            status.color = TEXT_MUTED
            page.update()
            await asyncio.sleep(0.2)  # Briefly show processing

            spinner.visible = False

            action = result.get("action", "unknown")
            spoken = result.get("text", "")

            if action == "start_analysis":
                status.value = "Starting analysis..."
                status.color = SUCCESS
            elif action == "new_analysis":
                status.value = "Starting new analysis..."
                status.color = SUCCESS
            elif action == "open_insights":
                status.value = "Opening insights..."
                status.color = SUCCESS
            elif action == "compare":
                status.value = "Opening comparison..."
                status.color = SUCCESS
            elif action == "show_roadmap":
                status.value = "Opening roadmap..."
                status.color = SUCCESS
            elif action == "show_patterns":
                status.value = "Opening patterns..."
                status.color = SUCCESS
            elif action == "go_home":
                status.value = "Going home..."
                status.color = SUCCESS
            elif action == "help":
                status.value = "Try: start analysis · open insights · go home"
                status.color = TEXT_MUTED
            elif action == "timeout":
                status.value = "I didn't hear anything."
                status.color = ERROR
            elif action == "unknown":
                status.value = f"Didn't recognize: {spoken}"
                status.color = ERROR
            else:
                status.value = "Voice service unavailable."
                status.color = ERROR

            page.update()

            if on_command:
                on_command(result)

        except Exception as error:
            is_listening = False
            spinner.visible = False
            status.value = f"Voice error: {error}"
            status.color = ERROR
            page.update()

        finally:
            is_listening = False
            button.disabled = False
            button.bgcolor = BG_INPUT
            button.scale = 1.0
            page.update()

    # Wrap button in a stack with pulse ring
    button_stack = ft.Stack(
        controls=[
            ft.Container(
                content=pulse_ring,
                alignment=ft.Alignment(0, 0),
                width=54,
                height=54,
            ),
            ft.Container(
                content=button,
                alignment=ft.Alignment(0, 0),
                width=48,
                height=48,
                on_click=lambda e: page.run_task(listen, e),
            ),
        ],
        width=48,
        height=48,
        alignment=ft.Alignment(0, 0),
    )

    return ft.Column(
        spacing=6,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            button_stack,
            status_row,
        ],
    )