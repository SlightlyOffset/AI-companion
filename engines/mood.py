import random
from responses.responses import get_respond
from actions import APPS

SASS_WEIGHT = 5
OBEDIENT_WEIGHT = 4

def is_command(user_input: str) -> bool:
    """Checks if the user is asking to open an app."""
    user_input = user_input.lower()
    return any(trigger in user_input for trigger in APPS.keys()) or "open" in user_input

def mood_engine(user_input: str):
    """
    Decides whether to act or just talk.
    Returns: (action_requested: bool, should_obey: bool, response_text: str)
    """
    user_is_asking_for_action = is_command(user_input)
    
    # Decide if we are being sassy or obedient
    mood = random.choices(["sass", "obedient"], weights=[SASS_WEIGHT, OBEDIENT_WEIGHT], k=1)[0]
    should_obey = (mood == "obedient")

    # If it's a command and we decide to be sassy, we roast them.
    # If it's just chat, we always get an LLM response to keep the conversation going.
    response_text = get_respond(mood, user_input)
    
    return user_is_asking_for_action, should_obey, response_text
