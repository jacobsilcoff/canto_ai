"""
Content Generator
Uses OpenAI API to generate learning unit content
"""
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
import os

from utils.jyutping import get_jyutping
from services.unit_service import save_unit
from services.srs_service import add_vocabulary
from generators.audio_generator import generate_unit_audio

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a Cantonese language course architect creating natural, conversational learning content.

LINGUISTIC GUIDELINES:
- Use natural, colloquial Hong Kong Cantonese
- Appropriate for beginner to low-intermediate learners
- Include sentence-final particles naturally (啊/呀/喇/喎/咩/呢/架/㗎)
- 6-8 sentence conversation with alternating speakers (A, B, A, B...)
- One sentence per turn

CHUNKING RULES (CRITICAL):
Each chunk must be the SMALLEST reusable grammatical unit:
- Separate numerals: "一" (one)
- Separate classifiers: "個" (measure word)
- Separate nouns: "人" (person)
- Separate verbs: "去" (go)
- Separate aspect markers: "咗" (completed action)
- Separate particles as their own chunks: "喇" (change of state)
- Characters must appear in order, verbatim

PARTICLE MEANINGS:
For sentence-final particles, provide their pragmatic function in parentheses:
- Example: "(softens tone)", "(seeking confirmation)", "(change of state)"

OUTPUT FORMAT - Valid JSON only:
{
  "title": "Topic Title",
  "topic_description": "Brief description",
  "conversation": [
    {
      "id": 0,
      "speaker": "A",
      "cantonese": "你好呀。",
      "english_natural": "Hello!",
      "chunks": [
        {"cantonese": "你", "english": "you"},
        {"cantonese": "好", "english": "good/well"},
        {"cantonese": "呀", "english": "(friendly particle)"}
      ]
    }
  ]
}"""


async def build_unit(topic: str) -> dict:
    """
    Generate a complete learning unit from a topic

    Args:
        topic: The topic/situation for the unit

    Returns:
        Complete unit dictionary
    """
    unit_id = str(int(time.time()))

    print(f"🎨 Designing unit: {topic}...")

    # Generate content with AI
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Create a unit about: {topic}"}
        ],
        temperature=0.7
    )

    unit_data = json.loads(response.choices[0].message.content)
    unit_data['id'] = unit_id

    # Trim title if too long
    if len(unit_data.get('title', '')) > 50:
        unit_data['title'] = topic[:50]

    # Add Jyutping to all text
    print("📝 Adding Jyutping...")
    for sentence in unit_data['conversation']:
        sentence['jyutping'] = get_jyutping(sentence['cantonese'])

        for chunk in sentence['chunks']:
            chunk['jyutping'] = get_jyutping(chunk['cantonese'])

    # Generate audio
    print("🔊 Generating audio...")
    await generate_unit_audio(unit_data, unit_id)

    # Save unit
    save_unit(unit_data)

    # Add to vocabulary
    all_chunks = []
    for sentence in unit_data['conversation']:
        all_chunks.extend(sentence['chunks'])
    add_vocabulary(all_chunks)

    print(f"✅ Unit '{unit_data['title']}' created successfully!")
    return unit_data