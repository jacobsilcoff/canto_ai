"""
Lesson Service
Generates lesson plans from unit data
"""
from typing import List, Dict
from core.constants import CHUNK_COLORS


def generate_lesson_plan(sentences: List[Dict], lesson_type: str = 'full') -> List[Dict]:
    """
    Generate a lesson plan from sentences

    Args:
        sentences: List of sentence dictionaries
        lesson_type: 'full' for complete lesson, 'quick' for intro only

    Returns:
        List of slide dictionaries
    """
    slides = []

    # Add color to chunks
    enriched_sentences = _enrich_sentences_with_colors(sentences)

    # 1. Introduction slide - show full dialogue
    slides.append({
        "type": "intro_dialogue",
        "data": enriched_sentences
    })

    if lesson_type == 'quick':
        return slides

    # 2. Build-up slides for each sentence
    for sentence in enriched_sentences:
        # Analysis slide - break down the sentence
        slides.append({
            "type": "analysis",
            "data": sentence
        })

        # Quiz slides for each chunk (skip punctuation)
        history = []
        for chunk in sentence['chunks']:
            if chunk['cantonese'] in {'。', '，', '？', '！', '.', ',', '?', '!'}:
                history.append(chunk)
                continue

            slides.append({
                "type": "quiz_recall",
                "target_chunks": [chunk],
                "target_english": chunk['english'],
                "context": list(history),
                "mode": "chunk"
            })
            history.append(chunk)

        # Full sentence recall quiz
        slides.append({
            "type": "quiz_recall",
            "target_chunks": sentence['chunks'],
            "target_english": sentence.get('english_natural', ''),
            "target_audio": sentence.get('audio_rel_path'),
            "context": [],
            "mode": "sentence"
        })

    return slides


def _enrich_sentences_with_colors(sentences: List[Dict]) -> List[Dict]:
    """Add colors to chunks for visual distinction"""
    enriched = []

    for sentence in sentences:
        sent_copy = sentence.copy()
        enriched_chunks = []

        for c_idx, chunk in enumerate(sentence.get('chunks', [])):
            chunk_copy = chunk.copy()
            chunk_copy['color'] = CHUNK_COLORS[c_idx % len(CHUNK_COLORS)]
            enriched_chunks.append(chunk_copy)

        sent_copy['chunks'] = enriched_chunks
        enriched.append(sent_copy)

    return enriched


def create_srs_slide(card: Dict) -> Dict:
    """Create a single SRS review slide from a vocab card"""
    return {
        "type": "quiz_recall",
        "target_chunks": [{
            "cantonese": card.get('cantonese', ''),
            "jyutping": card.get('jyutping', ''),
            "english": card.get('english', ''),
            "audio_rel_path": card.get('audio_rel_path'),
            "color": CHUNK_COLORS[0]
        }],
        "target_english": card.get('english', ''),
        "target_audio": card.get('audio_rel_path'),
        "context": [],
        "mode": "chunk"
    }