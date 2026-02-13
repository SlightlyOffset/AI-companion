import json
import os

def load_user_profile():
    """Loads the current user profile based on settings."""
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
    Constructs the full system prompt for the LLM, including character details,
    user profile, relationship status, and behavioral rules.
    """
    base_prompt = profile.get("system_prompt", "")

    # Companion Character Details
    backstory = profile.get("backstory", "Unknown.")
    mannerisms = ", ".join(profile.get("rp_mannerisms", []))
    info = profile.get("character_info", {})

    char_details = f"""[CHARACTER PROFILE]
Backstory: {backstory}
Age: {info.get('age', 'Unknown')}
Appearance: {info.get('appearance', 'Unknown')}
Likes: {', '.join(info.get('likes', []))}
Dislikes: {', '.join(info.get('dislikes', []))}
Mannerisms (use these in RP actions): {mannerisms}"""

    # User Profile Details
    user_profile = load_user_profile()
    user_details = ""
    if user_profile:
        u_info = user_profile.get("character_info", {})
        user_details = f"""[USER PROFILE (WHO YOU ARE TALKING TO)]
Name: {user_profile.get('name', 'User')}
Personality: {user_profile.get('personality_type', 'Unknown')}
Appearance: {u_info.get('appearance', 'Unknown')}
Pet: {u_info.get('pet', 'None')}
Likes: {', '.join(u_info.get('likes', []))}
Mannerisms to watch for: {', '.join(user_profile.get('rp_mannerisms', []))}"""

    system_content = f"{base_prompt}\n\n{char_details}\n\n{user_details}\n\n"
    system_content += f"[CONTEXT]\nRel: {rel_label} ({rel_score}/100)\nAction: {action_req}\nTone: {tone_mod}\n"

    if system_extra_info:
        system_content += f"\nNote: {system_extra_info}\n"

    rule = """
[BEHAVIOR RULES]
1. STAY IN CHARACTER at all times.
2. DIALOGUE vs ACTION: Always put narration/actions (*...*) on a SEPARATE LINE from spoken dialogue. 
   - Good: *She smiles.* 
     "Hello there."
   - Bad: *She smiles.* "Hello there."
3. MANNERISMS: Naturally weave your listed mannerisms into your actions.
4. SENTIMENT: End EVERY response with a sentiment tag: [REL: +X], [REL: -X], or [REL: 0] (Range: -5 to +5).
5. RELATIONSHIP: Your tone and willingness to help MUST reflect your current Relationship Score."""

    system_content += rule
    return system_content
