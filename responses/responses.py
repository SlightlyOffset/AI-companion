import ollama

def get_respond(mood: str, user_input: str, profile: dict) -> str:
    """
    Generates a response using the provided character profile.
    """
    base_prompt = profile.get("system_prompt", "You are a sassy AI.")
    
    if mood == "sass":
        prompt_modifier = "The user has asked you to do something. REFUSE it in character. Be mean, creative, and unfiltered."
    else:
        prompt_modifier = "The user has asked you to do something. AGREE to it, but with a heavy dose of sarcasm and complaining."

    try:
        # Using the model of your choice - suggest dolphin-llama3 for unfiltered RP
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': f"{base_prompt}\n\nCURRENT CONTEXT: {prompt_modifier}"},
            {'role': 'user', 'content': user_input},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Brain error: {str(e)}. (Is Ollama running?)"