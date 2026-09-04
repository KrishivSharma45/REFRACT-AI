def parse_voice_command(command: str):
    """Map a spoken phrase to a REFRACT action.

    Recognised actions:
      start_analysis, new_analysis, open_insights, compare,
      show_roadmap, show_patterns, go_home, help, unknown
    """

    if not command:
        return {"action": "unknown", "text": ""}

    text = command.lower().strip()

    def has(*phrases):
        return any(p in text for p in phrases)

    if has("start analysis", "begin analysis", "analyze my application",
           "analyse my application", "start analyzing", "start analysing",
           "run analysis", "run the analysis"):
        return {"action": "start_analysis", "text": text}

    if has("new analysis", "analyze again", "analyse again", "start over",
           "start a new analysis"):
        return {"action": "new_analysis", "text": text}

    if has("open insights", "show insights", "go to insights", "view insights",
           "insights page"):
        return {"action": "open_insights", "text": text}

    if has("compare applications", "compare application", "compare analyses",
           "compare my applications", "comparison"):
        return {"action": "compare", "text": text}

    if has("show roadmap", "open roadmap", "my roadmap", "improvement roadmap",
           "personal roadmap"):
        return {"action": "show_roadmap", "text": text}

    if has("show patterns", "open patterns", "recurring patterns", "my patterns",
           "detect patterns"):
        return {"action": "show_patterns", "text": text}

    if has("go home", "take me home", "home page", "back home", "go to home"):
        return {"action": "go_home", "text": text}

    if has("help", "what can you do", "how does this work", "what can i say"):
        return {"action": "help", "text": text}

    return {"action": "unknown", "text": text}
