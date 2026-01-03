import os
import base64
from config import AUDIO_BASE


def get_b64_audio(rel_path):
    """Converts audio file to base64 string for HTML embedding."""
    if not rel_path: return None  # <--- Fix: Handle None/Empty paths safely

    full_path = os.path.join(AUDIO_BASE, rel_path)
    if os.path.exists(full_path) and os.path.isfile(full_path):
        try:
            with open(full_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None
    return None