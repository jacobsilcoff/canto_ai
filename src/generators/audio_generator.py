"""
Audio Generator
Generate TTS audio for unit content using edge-tts
"""
import asyncio
import os
import edge_tts
from core.constants import VOICES
from utils.audio import ensure_audio_dir


async def generate_audio_file(text: str, filepath: str, voice: str):
    """
    Generate a single audio file using TTS

    Args:
        text: Text to synthesize
        filepath: Output file path
        voice: Voice identifier (e.g., "zh-HK-HiuGaaiNeural")
    """
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
    except Exception as e:
        print(f"Error generating audio {filepath}: {e}")


async def generate_unit_audio(unit_data: dict, unit_id: str):
    """
    Generate all audio files for a unit

    Args:
        unit_data: Unit dictionary with conversation data
        unit_id: Unique unit identifier
    """
    audio_dir = ensure_audio_dir(unit_id)
    tasks = []

    for s_idx, sentence in enumerate(unit_data['conversation']):
        speaker = sentence.get('speaker', 'A')
        voice = VOICES.get(speaker, VOICES['A'])

        # Generate sentence audio
        s_filename = f"sent_{s_idx}.mp3"
        s_path = os.path.join(audio_dir, s_filename)
        sentence['audio_rel_path'] = f"{unit_id}/{s_filename}"

        tasks.append(generate_audio_file(sentence['cantonese'], s_path, voice))

        # Generate chunk audio
        for c_idx, chunk in enumerate(sentence.get('chunks', [])):
            c_filename = f"chunk_{s_idx}_{c_idx}.mp3"
            c_path = os.path.join(audio_dir, c_filename)
            chunk['audio_rel_path'] = f"{unit_id}/{c_filename}"

            tasks.append(generate_audio_file(chunk['cantonese'], c_path, voice))

    # Generate all audio in parallel
    await asyncio.gather(*tasks)


async def regenerate_audio(unit_data: dict):
    """
    Regenerate audio for an existing unit

    Args:
        unit_data: Unit dictionary
    """
    unit_id = unit_data.get('id')
    if not unit_id:
        raise ValueError("Unit must have an 'id' field")

    await generate_unit_audio(unit_data, unit_id)