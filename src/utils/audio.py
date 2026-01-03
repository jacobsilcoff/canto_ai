"""
Audio Utilities
Handle audio file encoding and conversion
"""
import os
import base64
from core.constants import AUDIO_DIR


def get_b64_audio(rel_path: str) -> str:
    """
    Convert audio file to base64 string for HTML embedding

    Args:
        rel_path: Relative path to audio file (e.g., "unit_id/chunk_0_1.mp3")

    Returns:
        Base64 encoded audio string, or None if file not found
    """
    if not rel_path:
        return None

    full_path = os.path.join(AUDIO_DIR, rel_path)

    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return None

    try:
        with open(full_path, "rb") as f:
            audio_data = f.read()
            return base64.b64encode(audio_data).decode('utf-8')
    except Exception as e:
        print(f"Error encoding audio {rel_path}: {e}")
        return None


def ensure_audio_dir(unit_id: str) -> str:
    """
    Ensure audio directory exists for a unit

    Args:
        unit_id: Unit identifier

    Returns:
        Path to the unit's audio directory
    """
    unit_audio_dir = os.path.join(AUDIO_DIR, unit_id)
    os.makedirs(unit_audio_dir, exist_ok=True)
    return unit_audio_dir