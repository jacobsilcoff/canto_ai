import json
import os
import time
from config import VOCAB_PATH


def get_due_cards():
    """Returns a list of words due for review."""
    if not os.path.exists(VOCAB_PATH): return []
    try:
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab = json.load(f)
        now = time.time()
        return [w for w in vocab if w.get('next_review', 0) <= now]
    except:
        return []


def update_card(word_canto, quality):
    """
    Updates the interval for a card based on user feedback.
    quality: 0 (Wrong), 3 (Good), 5 (Easy)
    """
    if not os.path.exists(VOCAB_PATH): return

    with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
        vocab = json.load(f)

    for word in vocab:
        if word['cantonese'] == word_canto:
            if quality == 0:
                word['interval'] = 1
                word['reps'] = 0
            else:
                multiplier = 2.0 if quality == 5 else 1.5
                word['interval'] = max(1, word.get('interval', 0) * multiplier)
                word['reps'] = word.get('reps', 0) + 1

            # Update next review time (current time + days in seconds)
            word['next_review'] = time.time() + (word['interval'] * 86400)
            break

    with open(VOCAB_PATH, 'w', encoding='utf-8') as f:
        json.dump(vocab, f, indent=2, ensure_ascii=False)