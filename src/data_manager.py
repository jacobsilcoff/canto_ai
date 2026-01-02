import json
import os
from config import DATA_DIR, PROGRESS_PATH


def load_unit(filename):
    """Loads a specific unit JSON."""
    try:
        with open(os.path.join(DATA_DIR, filename), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_all_units():
    """Returns a list of all unit filenames."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]


def save_progress(unit_id, lesson_key, slide_idx):
    """Saves user progress for a specific lesson."""
    if not os.path.exists(PROGRESS_PATH):
        data = {}
    else:
        try:
            with open(PROGRESS_PATH, 'r') as f:
                data = json.load(f)
        except:
            data = {}

    if unit_id not in data: data[unit_id] = {}
    data[unit_id][lesson_key] = slide_idx

    with open(PROGRESS_PATH, 'w') as f:
        json.dump(data, f)


def get_progress(unit_id, lesson_key):
    """Retrieves progress index."""
    if not os.path.exists(PROGRESS_PATH): return 0
    try:
        with open(PROGRESS_PATH, 'r') as f:
            data = json.load(f)
        return data.get(unit_id, {}).get(lesson_key, 0)
    except:
        return 0