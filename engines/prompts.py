"""
System prompt construction and character context management.
Builds the 'brain' instructions for the LLM based on character and user profiles.
"""

import json
import os

def load_user_profile():
    """
    Loads the currently selected user profile from the user_profiles directory.

    Returns:
        dict: The user profile data, or None if loading fails.
    """
    from engines.config import get_setting
    user_filename = get_setting("current_user_profile", "Manganese.json")
    user_path = os.path.join("user_profiles", user_filename)

    if os.path.exists(user_path):
        try:
            with open(user_path, "r", encoding="UTF-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def build_system_prompt(profile: dict, rel_score: int, rel_label: str, action_req: str, tone_mod: str, system_extra_info: str = None) -> str:
    """
    Constructs the master system prompt for the LLM.
    Combines character backstory, mannerisms, user details, and behavioral rules.

    Args:
        profile (dict): The active companion's profile data.
        rel_score (int): Current relationship score (-100 to 100).
        rel_label (str): Textual label for the relationship (e.g., 'Soulmate').
        action_req (str): Instruction on whether to obey or refuse requests.
        tone_mod (str): Instruction on the tone of the response.
        system_extra_info (str): Temporary context/notes for this specific turn.

    Returns:
        str: The full system instruction string.
    """
    base_prompt = profile.get("system_prompt", "")

    # 1. Companion Character Details
    backstory = profile.get("backstory", "Unknown.")
    mannerisms = ", ".join(profile.get("rp_mannerisms", []))
    info = profile.get("character_info", {})

    char_details = f"""
[CHARACTER PROFILE]
Name: {profile.get('name', 'Unknown')}
Alternate Names: {profile.get('alt_names', 'None')}
Personality Type: {profile.get('personality_type', 'Unknown')}
Backstory: {backstory}
Age: {info.get('age', 'Unknown')}
Appearance: {info.get('appearance', 'Unknown')}
Likes: {', '.join(info.get('likes', []))}
Dislikes: {', '.join(info.get('dislikes', []))}
Mannerisms (use these in RP actions): {mannerisms}
"""

    # 2. User Profile Details (Who the AI thinks it's talking to)
    user_profile = load_user_profile()
    user_details = ""
    if user_profile:
        u_info = user_profile.get("character_info", {})
        user_details = f"""
[USER PROFILE (WHO YOU ARE TALKING TO)]
Name: {user_profile.get('name', 'User')}
Personality: {user_profile.get('personality_type', 'Unknown')}
Appearance: {u_info.get('appearance', 'Unknown')}
Pet: {u_info.get('pet', 'None')}
Likes: {', '.join(u_info.get('likes', []))}
Mannerisms to watch for: {', '.join(user_profile.get('rp_mannerisms', []))}
"""

    # 3. Dynamic Context (Relationship and Tone)
    system_content = f"""{base_prompt}

{char_details}
{user_details}

[CONTEXT]
Rel: {rel_label} ({rel_score}/100)
Action: {action_req}
Tone: {tone_mod}
"""

    # 4. Global Behavioral Rules for RP Immersion
    rule = """
[BEHAVIOR RULES]
1. STAY IN CHARACTER at all times.
2. DIALOGUE vs ACTION: Always put narration/actions (*...*) on a SEPARATE LINE from spoken dialogue.
   - Good: *She smiles.* \n "Hello there."
   - Bad: *She smiles.* "Hello there."
3. MANNERISMS: Naturally weave your listed mannerisms into your actions.
4. SENTIMENT: End EVERY response with a sentiment tag: [REL: +X], [REL: -X], or [REL: 0] (Range: -5 to +5).
5. RELATIONSHIP: Your tone and willingness to help MUST reflect your current Relationship Score.
"""

    if system_extra_info:
        system_content += f"Note: {system_extra_info}\n"

    system_content += f"{rule}"

    return system_content
