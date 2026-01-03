"""
Unit Service
Handles loading, saving, and listing units
"""
import json
import os
from typing import List, Dict, Optional
from core.constants import DATA_DIR


def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_all_units() -> List[str]:
    """Get list of all unit filenames"""
    ensure_data_dir()
    return sorted(
        [f for f in os.listdir(DATA_DIR) if f.endswith('.json')],
        reverse=True  # Newest first
    )


def load_unit(filename: str) -> Optional[Dict]:
    """Load a specific unit by filename"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading unit {filename}: {e}")
        return None


def save_unit(unit_data: Dict) -> bool:
    """Save a unit to disk"""
    try:
        ensure_data_dir()
        unit_id = unit_data.get('id')
        if not unit_id:
            raise ValueError("Unit must have an 'id' field")

        filepath = os.path.join(DATA_DIR, f"{unit_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(unit_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving unit: {e}")
        return False


def delete_unit(filename: str) -> bool:
    """Delete a unit file"""
    try:
        filepath = os.path.join(DATA_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception as e:
        print(f"Error deleting unit {filename}: {e}")
        return False


def get_unit_stats(unit: Dict) -> Dict:
    """Get statistics for a unit"""
    return {
        'total_sentences': len(unit.get('conversation', [])),
        'total_chunks': sum(len(s.get('chunks', [])) for s in unit.get('conversation', [])),
        'speakers': len(set(s.get('speaker', 'A') for s in unit.get('conversation', [])))
    }