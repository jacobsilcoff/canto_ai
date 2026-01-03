"""
Interactive Lesson Player Component
Renders Mango-style interactive lessons with modern UI
"""
import json
import streamlit.components.v1 as components
from utils.audio import get_b64_audio
from core.constants import CHUNK_COLORS, PLAYER_HEIGHT, PLAYER_HEIGHT_SRS

def render_player(slides_data: list, key: str, srs_mode: bool = False):
    """
    Render the interactive lesson player

    Args:
        slides_data: List of slide dictionaries
        key: Unique key for the component
        srs_mode: If True, simplified UI for review
    """
    js_slides = _process_slides(slides_data)
    json_payload = json.dumps(js_slides)

    # Dynamic styling based on mode
    footer_style = "display:none !important;" if srs_mode else ""
    container_padding = "20px" if srs_mode else "100px"

    html_code = _generate_html(json_payload, footer_style, container_padding)

    height = PLAYER_HEIGHT_SRS if srs_mode else PLAYER_HEIGHT
    components.html(html_code, height=height, scrolling=False)

def _process_slides(slides_data: list) -> list:
    """Process slides and convert to JS-compatible format"""
    js_slides = []

    for slide in slides_data:
        slide_obj = {'type': slide['type'], 'content': {}}

        if slide['type'] in ['intro_dialogue', 'analysis']:
            slide_obj['content']['items'] = _process_dialogue_items(slide)
        elif slide['type'] == 'quiz_recall':
            slide_obj['content'] = _process_quiz_content(slide)

        js_slides.append(slide_obj)

    return js_slides

def _process_dialogue_items(slide: dict) -> list:
    """Process dialogue/analysis slide items"""
    items = []
    data_source = slide['data'] if isinstance(slide['data'], list) else [slide['data']]

    for line in data_source:
        items.append({
            "speaker": line.get('speaker', 'A'),
            "english_natural": line.get('english_natural', ''),
            "full_audio_b64": get_b64_audio(line.get('audio_rel_path')),
            "chunks": _process_chunks(line.get('chunks', []))
        })

    return items

def _process_quiz_content(slide: dict) -> dict:
    """Process quiz slide content"""
    content = {
        'target_pills': _process_chunks(slide.get('target_chunks', [])),
        'target_english': slide.get('target_english', ''),
        'context': [{"cantonese": c['cantonese']} for c in slide.get('context', [])]
    }

    # Handle audio for quiz
    target_audio = slide.get('target_audio')
    if target_audio:
        content['audio_b64'] = get_b64_audio(target_audio)
    elif content['target_pills']:
        content['audio_b64'] = content['target_pills'][0].get('audio_b64')
    else:
        content['audio_b64'] = None

    return content

def _process_chunks(chunk_list: list) -> list:
    """Process chunks with audio and colors"""
    processed = []

    for i, chunk in enumerate(chunk_list):
        color = chunk.get('color', CHUNK_COLORS[i % len(CHUNK_COLORS)])
        audio_path = chunk.get('audio_rel_path')

        processed.append({
            "cantonese": chunk.get('cantonese', ''),
            "jyutping": chunk.get('jyutping', ''),
            "english": chunk.get('english', ''),
            "audio_b64": get_b64_audio(audio_path) if audio_path else None,
            "color": color
        })

    return processed

def _generate_html(json_payload: str, footer_style: str, container_padding: str) -> str:
    """Generate the complete HTML for the player"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/wavesurfer.js@7.5.3/dist/wavesurfer.min.js"></script>
    <style>
        {_get_styles(footer_style, container_padding)}
    </style>
</head>
<body>
    <div id="app" class="scroll-viewport"></div>
    
    <div class="footer-nav">
        <button id="prevBtn" class="nav-btn" onclick="changeSlide(-1)">
            <span style="font-size:1.2em;">←</span> Back
        </button>
        <div id="progress" class="progress-text">1 / 1</div>
        <button id="nextBtn" class="nav-btn nav-btn-primary" onclick="changeSlide(1)">
            Next <span style="font-size:1.2em;">→</span>
        </button>
    </div>
    
    <script>
        {_get_javascript(json_payload)}
    </script>
</body>
</html>"""

def _get_styles(footer_style: str, container_padding: str) -> str:
    """Import styles from player_styles module"""
    from components.player_styles import get_styles
    return get_styles(footer_style, container_padding)

def _get_javascript(json_payload: str) -> str:
    """Import JavaScript from player_javascript module"""
    from components.player_javascript import get_javascript
    return get_javascript(json_payload)