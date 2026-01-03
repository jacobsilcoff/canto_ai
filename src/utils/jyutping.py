"""
Jyutping Utilities
Convert Cantonese characters to Jyutping romanization
"""
import pycantonese


def get_jyutping(text: str) -> str:
    """
    Convert Cantonese text to Jyutping romanization

    Args:
        text: Cantonese characters

    Returns:
        Space-separated Jyutping string (e.g., "nei5 hou2")
    """
    try:
        # Get character-to-jyutping mappings
        characters = pycantonese.characters_to_jyutping(text)

        # Join into space-separated string
        jyutping_str = " ".join([char[1] for char in characters])

        return jyutping_str
    except Exception as e:
        print(f"Error converting to Jyutping: {e}")
        return ""


def validate_jyutping(jyutping: str) -> bool:
    """
    Validate if a string is valid Jyutping

    Args:
        jyutping: String to validate

    Returns:
        True if valid, False otherwise
    """
    # Basic validation: check for number at end of each syllable
    syllables = jyutping.split()
    for syllable in syllables:
        if not syllable or not syllable[-1].isdigit():
            return False
    return True