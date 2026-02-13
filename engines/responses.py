import re
import json
import ollama
import requests
from datetime import datetime
from engines.memory import save_conversation, load_conversation, get_last_timestamp
from engines.config import get_setting

def apply_mood_decay(profile_path: str, profile_name: str):
    """
    Calculates time passed since last interaction and decays relationship score
    towards 0 (Neutral) proportionally.
    """
    last_time = get_last_timestamp(profile_name)
    if not last_time:
        return 0, 0

    now = datetime.now()
    diff = now - last_time
    hours_passed = diff.total_seconds() / 3600

    if hours_passed < (5 / 60):
        return 0, 0

    try:
        with open(profile_path, "r", encoding="UTF-8") as f:
            data = json.load(f)

        current_score = data.get("relationship_score", 0)
        if current_score == 0:
            return 0, 0

        decay_factor = 0.95
        new_score_float = current_score * (decay_factor ** hours_passed)
        new_score = int(round(new_score_float))

        if current_score != new_score:
            decay_amount = abs(current_score - new_score)
            data["relationship_score"] = new_score
            with open(profile_path, "w", encoding="UTF-8") as f:
                json.dump(data, f, indent=4)
            return decay_amount, new_score

    except Exception as e:
        print(f"Error applying mood decay: {e}")

    return 0, 0


def update_profile_score(profile_path: str, score_change: int):
    """Update the relationship score in the profile JSON file."""
    try:
        with open(profile_path, "r", encoding="UTF-8") as f:
            data = json.load(f)

        current_score = data.get("relationship_score", 0)
        new_score = max(-100, min(100, current_score + score_change))
        data["relationship_score"] = new_score

        with open(profile_path, "w", encoding="UTF-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Error updating profile score: {e}")


def get_respond_stream(user_input: str, profile: dict, should_obey: bool | None = None, profile_path: str = None, system_extra_info: str = None):
    """
    Generates a streaming response.
    user_input: The clean user text (saved to history).
    system_extra_info: Temporary instructions (NOT saved to history).
    """
    name = profile.get("name")
    model = profile.get("llm_model", get_setting("default_llm_model", "llama3"))
    remote_url = get_setting("remote_llm_url")

    # Load history without system timestamps for the prompt
    history = load_conversation(name, filter_system=True)
    limit = get_setting("history_limit", 15)
    history = history[-limit:] if history and limit > 0 else history

    # Setup context
    base_prompt = profile.get("system_prompt")
    rel_score = profile.get("relationship_score", 0)

    if rel_score >= 80: rel_label = "Soulmate / Bestie"
    elif rel_score >= 40: rel_label = "Close Friend"
    elif rel_score >= 15: rel_label = "Friendly / Liked"
    elif rel_score >= -15: rel_label = "Neutral / Acquaintance"
    elif rel_score >= -40: rel_label = "Annoyance / Disliked"
    elif rel_score >= -80: rel_label = "Hostile / Enemy"
    else: rel_label = "Arch-Nemesis / Despised"

    if should_obey is not None:
        if not should_obey:
            action_req = "MUST REFUSE the user's request."
            tone_mod = profile.get("bad_prompt_modifyer", "Refuse creatively.")
        else:
            action_req = "MUST AGREE to the user's request."
            tone_mod = profile.get("good_prompt_modifyer", "Agree and assist.")
    else:
        action_req = "Respond normally."
        tone_mod = "Maintain a balanced tone."

    system_content = f"""{base_prompt}

[CONTEXT]
Rel: {rel_label} ({rel_score}/100)
Action: {action_req}
Tone: {tone_mod}
"""
    if system_extra_info:
        system_content += f"Note: {system_extra_info}\n"

    system_content += "\n[RULES]\n1. Stay in character.\n2. End with sentiment tag: [REL: +X], [REL: -X], or [REL: 0] (-5 to +5).\n"

    messages = [{'role': 'system', 'content': system_content}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_input})

    full_reply = ""
    buffer = ""

    try:
        if remote_url:
            full_url = f"{remote_url.rstrip('/')}/chat"
            payload = {
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 1024
            }
            response = requests.post(full_url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            stream = response.iter_content(chunk_size=None, decode_unicode=True)
        else:
            ollama_stream = ollama.chat(model=model, messages=messages, stream=True)
            def ollama_gen():
                for chunk in ollama_stream:
                    yield chunk['message']['content']
            stream = ollama_gen()

        for content in stream:
            full_reply += content
            buffer += content

            if '[' in buffer:
                if ']' in buffer:
                    if re.search(r'\[REL:\s*[+-]?\d+\]', buffer):
                        buffer = re.sub(r'\[REL:\s*[+-]?\d+\]', '', buffer)
                        if buffer:
                            yield buffer
                            buffer = ""
                    else:
                        yield buffer
                        buffer = ""
                else:
                    if len(buffer) > 20:
                        yield buffer
                        buffer = ""
            else:
                yield buffer
                buffer = ""

        if buffer:
            yield buffer

        # Extract score and clean reply
        score_change = 0
        match = re.search(r'\[REL:\s*([+-]?\d+)\]', full_reply)
        if match:
            try:
                score_change = int(match.group(1))
                reply = re.sub(r'\[REL:\s*[+-]?\d+\]', '', full_reply).strip()
            except ValueError:
                reply = full_reply
        else:
            reply = full_reply

        # Perform updates
        if profile_path and score_change != 0:
            update_profile_score(profile_path, score_change)

        # Save clean history
        # Reload full history (with timestamps) to append and save
        full_history = load_conversation(name, filter_system=False)
        full_history.append({'role': 'user', 'content': user_input})
        full_history.append({'role': 'assistant', 'content': reply})
        save_conversation(name, full_history)

    except Exception as e:
        yield f"\n[BRAIN ERROR] {str(e)}"


def get_respond(user_input: str, profile: dict, should_obey: bool = True, profile_path: str = None) -> str:
    full_response = ""
    for chunk in get_respond_stream(user_input, profile, should_obey, profile_path):
        full_response += chunk
    return full_response
