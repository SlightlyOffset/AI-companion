import ollama

def get_respond(mood: str, user_input: str, profile: dict, should_obey: bool = True) -> str:
    """
    Generates a response using the provided character profile.
    """
    base_prompt = profile.get("system_prompt")

    if not should_obey:
        prompt_modifier = profile.get("bad_prompt_modifyer", "REFUSE the request creatively and in character.")
        strict_instruction = "IMPORTANT: You MUST REFUSE the user's request. Do not help them."
    else:
        prompt_modifier = profile.get("good_prompt_modifyer", "AGREE to the request politely.")
        strict_instruction = "IMPORTANT: You MUST AGREE to help the user. Do not refuse."

    try:
        # Using the model of your choice
        response = ollama.chat(model='llama3', messages=[
            {'role': 'system', 'content': f"{base_prompt}\n\n{prompt_modifier}\n\n{strict_instruction}"},
            {'role': 'user', 'content': user_input},
        ])
        return response['message']['content']
    except Exception as e:
        return f"Brain error: {str(e)}. (Is Ollama running?)"