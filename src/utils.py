import os
import base64
from config import AUDIO_BASE

def get_b64_audio(rel_path):
    """Converts audio file to base64 string for HTML embedding."""
    full_path = os.path.join(AUDIO_BASE, rel_path)
    if os.path.exists(full_path):
        with open(full_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None