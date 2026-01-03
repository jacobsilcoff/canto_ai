"""
Progress Service
Track user progress through lessons
"""
import json
import os
from typing import Dict, Optional
from core.constants import PROGRESS_PATH

def ensure_progress_file():
    """Ensure progress file exists"""
    if not os.path.exists(PROGRESS_PATH):
        os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
        with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
            json.dump({}, f)

def save_lesson_progress(unit_id: str, lesson_key: str, completed: bool = True):
    """
    Save progress for a specific lesson
    
    Args:
        unit_id: Unit identifier
        lesson_key: Lesson identifier (e.g., "lesson_1")
        completed: Whether the lesson was completed
    """
    ensure_progress_file()
    
    try:
        with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    
    if unit_id not in data:
        data[unit_id] = {}
    
    data[unit_id][lesson_key] = {
        'completed': completed,
        'last_accessed': __import__('time').time()
    }
    
    with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_lesson_progress(unit_id: str, lesson_key: str) -> Dict:
    """
    Get progress for a specific lesson
    
    Args:
        unit_id: Unit identifier
        lesson_key: Lesson identifier
    
    Returns:
        Dict with 'completed' and 'last_accessed' keys, or empty dict
    """
    ensure_progress_file()
    
    try:
        with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(unit_id, {}).get(lesson_key, {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_unit_progress(unit_id: str) -> Dict:
    """
    Get all progress for a unit
    
    Args:
        unit_id: Unit identifier
    
    Returns:
        Dict of lesson progress
    """
    ensure_progress_file()
    
    try:
        with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get(unit_id, {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def get_unit_completion_stats(unit_id: str, total_lessons: int) -> Dict:
    """
    Get completion statistics for a unit
    
    Args:
        unit_id: Unit identifier
        total_lessons: Total number of lessons in unit
    
    Returns:
        Dict with 'completed' and 'total' keys
    """
    progress = get_unit_progress(unit_id)
    completed = sum(1 for lesson_data in progress.values() 
                   if lesson_data.get('completed', False))
    
    return {
        'completed': completed,
        'total': total_lessons,
        'percentage': (completed / total_lessons * 100) if total_lessons > 0 else 0
    }

def mark_lesson_started(unit_id: str, lesson_key: str):
    """
    Mark that a lesson has been started (but not necessarily completed)
    
    Args:
        unit_id: Unit identifier
        lesson_key: Lesson identifier
    """
    save_lesson_progress(unit_id, lesson_key, completed=False)

def clear_unit_progress(unit_id: str):
    """
    Clear all progress for a unit
    
    Args:
        unit_id: Unit identifier
    """
    ensure_progress_file()
    
    try:
        with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if unit_id in data:
            del data[unit_id]
        
        with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except (FileNotFoundError, json.JSONDecodeError):
        pass