import random
from engines.responses import get_respond
from engines.actions import APPS

# Base weights for mood decision
SASS_WEIGHT = 1
OBEDIENT_WEIGHT = 2

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
