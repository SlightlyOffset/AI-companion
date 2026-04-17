import re
from rich.markup import escape


def format_summary_text(summary: str) -> str:
    """Convert summary markdown-like text into safe Rich markup."""
    text = escape(summary)
    text = re.sub(r"^##\s+(.*)$", r"[b][u]\1[/u][/b]", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", r"[b]\1[/b]", text, flags=re.DOTALL)
    return text.replace("*", "•")


def format_roleplay_text(
    text: str,
    role: str,
    user_name: str = "User",
    character_name: str = "Assistant",
    user_speech_color: str = "yellow",
    assistant_speech_color: str = "yellow",
) -> str:
    """Format RP text for display in the TUI chat bubbles."""
    if not text:
        return ""

    text = text.replace("{{user}}", user_name).replace("{{char}}", character_name)
    text = text.replace("{{User}}", user_name).replace("{{Char}}", character_name)
    text = re.sub(r"\[SCENE:\s*.*?\]", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"[b]\1[/b]", text, flags=re.DOTALL)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"[i][dim]\1[/dim][/i]", text, flags=re.DOTALL)

    speech_color = assistant_speech_color if role == "assistant" else user_speech_color
    return re.sub(r'["“](.*?)["”]', fr'[{speech_color}]"\1"[/{speech_color}]', text, flags=re.DOTALL)


def get_tts_split_points(text: str) -> list[int]:
    """
    Find safe split points for TTS chunking.
    Splits on asterisk boundaries and sentence punctuation outside narration markers.
    """
    points: list[int] = []
    in_asterisks = False
    for index, char in enumerate(text):
        if char == "*":
            in_asterisks = not in_asterisks
            points.append(index + 1)
            continue

        if in_asterisks:
            continue

        if char in ".!?\n":
            if char == "." and index + 1 < len(text) and text[index + 1] == ".":
                continue
            if char == "." and index > 0 and text[index - 1] == ".":
                continue
            points.append(index + 1)
    return points
