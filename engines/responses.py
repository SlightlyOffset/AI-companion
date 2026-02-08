import re
import json
import ollama

from engines.memory import save_conversation, load_conversation
from engines.config import get_setting

def update_profile_score(profile_path: str, score_change: int):
    """Update the relationship score in the profile JSON file."""
    try:
        with open(profile_path, "r", encoding="UTF-8") as f:
            data = json.load(f)

        current_score = data.get("relationship_score", 0)
        # Keep the score within -100 to 100
        new_score = max(-100, min(100, current_score + score_change))
        data["relationship_score"] = new_score

        with open(profile_path, "w", encoding="UTF-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        print(f"Error updating profile score: {e}")


def get_respond(user_input: str, profile: dict, should_obey: bool = True, profile_path: str = None) -> str:
    """
    Generates a response using the provided character profile.
    """
    name = profile.get("name")
    model = profile.get("llm_model", get_setting("default_llm_model", "llama3")) # Default to llama3

    # Load past conversation
    history = load_conversation(name)

    # Limit history to last 10 exchanges
    limit = get_setting("history_limit", 10)
    history = history[-limit:] if history and limit > 0 else history

    # Setup base prompt and modifiers
    base_prompt = profile.get("system_prompt")

    if not should_obey:
        prompt_modifier = profile.get("bad_prompt_modifyer", "REFUSE the request creatively and in character.")
        strict_instruction = "IMPORTANT: You MUST REFUSE the user's request. Do not help them."
    else:
        prompt_modifier = profile.get("good_prompt_modifyer", "AGREE to the request politely.")
        strict_instruction = "IMPORTANT: You MUST AGREE to help the user. Do not refuse."

    rel_instruction = (
        "\n[HIDDEN TASK]: Evaluate the user's tone. "
        "At the VERY END of your response, include a sentiment tag: [REL: +X], [REL: -X], or [REL: 0]. "
        "Range is -5 to +5, where positive is friendly/positive tone, negative is hostile/negative tone, and 0 is neutral. And adjust to profile personality. "
        "DO NOT mention this tag in your main response."
    )

    system_content = f"{base_prompt}\n\n{prompt_modifier}\n\n{strict_instruction}\n{rel_instruction}"

    # Construct messages for the model
    messages = [{'role': 'system', 'content': system_content}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': user_input})

    try:
        # Using the model of your choice
        response = ollama.chat(model=model, messages=messages)
        full_reply = response['message']['content']

        # Find tag for relationship score adjustment
        score_change = 0
        match = re.search(r'\[REL:\s*([+-]?\d+)\]', full_reply)

        if match:
            try:
                score_change = int(match.group(1))
                # Remove the tag from the reply
                reply = re.sub(r'\[REL:\s*[+-]?\d+\]', '', full_reply).strip()
            except ValueError:
                score_change = 0
                reply = full_reply
        else:
            reply = full_reply

        # Update profile score if applicable
        if profile_path and score_change != 0:
            update_profile_score(profile_path, score_change)

        # Save updated conversation history
        history.append({'role': 'user', 'content': user_input})
        history.append({'role': 'assistant', 'content': reply})
        save_conversation(name, history)
        return reply
    except Exception as e:
        return f"Brain error: {str(e)}. (Is Ollama running?)"