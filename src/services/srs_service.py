"""
SRS (Spaced Repetition System) Service
Manages vocabulary review scheduling
"""
import json
import os
import time
import re
from typing import List, Dict
from core.constants import VOCAB_PATH, SRS_INTERVALS, PUNCTUATION


def ensure_vocab_file():
    """Ensure vocab file exists"""
    if not os.path.exists(VOCAB_PATH):
        os.makedirs(os.path.dirname(VOCAB_PATH), exist_ok=True)
        with open(VOCAB_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)


def get_due_cards() -> List[Dict]:
    """Get all cards due for review"""
    ensure_vocab_file()

    try:
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab = json.load(f)

        now = time.time()
        return [card for card in vocab if card.get('next_review', 0) <= now]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def get_vocab_stats() -> Dict:
    """Get vocabulary statistics"""
    ensure_vocab_file()

    try:
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab = json.load(f)

        now = time.time()
        due = sum(1 for card in vocab if card.get('next_review', 0) <= now)

        return {
            'total': len(vocab),
            'due': due,
            'learned': sum(1 for card in vocab if card.get('reps', 0) > 0)
        }
    except (FileNotFoundError, json.JSONDecodeError):
        return {'total': 0, 'due': 0, 'learned': 0}


def update_card(cantonese: str, quality: int):
    """
    Update card review data based on user performance

    Args:
        cantonese: The Cantonese word
        quality: 0 (wrong), 3 (good), 5 (easy)
    """
    ensure_vocab_file()

    try:
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab = json.load(f)

        for card in vocab:
            if card['cantonese'] == cantonese:
                if quality == 0:  # Wrong
                    card['interval'] = SRS_INTERVALS['wrong']
                    card['reps'] = 0
                else:  # Good or Easy
                    multiplier = SRS_INTERVALS['easy'] if quality == 5 else SRS_INTERVALS['good']
                    card['interval'] = max(1, card.get('interval', 0) * multiplier)
                    card['reps'] = card.get('reps', 0) + 1

                # Schedule next review
                card['next_review'] = time.time() + (card['interval'] * 86400)
                break

        with open(VOCAB_PATH, 'w', encoding='utf-8') as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error updating card: {e}")


def add_vocabulary(chunks: List[Dict]):
    """Add new vocabulary from chunks, filtering punctuation"""
    ensure_vocab_file()

    try:
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        vocab = []

    existing = {card['cantonese'] for card in vocab}
    punct_pattern = re.compile(r'^[^\w\s\u4e00-\u9fff]+$')

    for chunk in chunks:
        canto = chunk['cantonese']

        # Skip if exists, is punctuation, or matches punct pattern
        if canto in existing or canto in PUNCTUATION or punct_pattern.match(canto):
            continue

        vocab.append({
            "cantonese": canto,
            "jyutping": chunk.get('jyutping', ''),
            "english": chunk.get('english', ''),
            "audio_rel_path": chunk.get('audio_rel_path'),
            "learned_date": time.time(),
            "next_review": time.time(),
            "interval": 0,
            "reps": 0
        })

    with open(VOCAB_PATH, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)