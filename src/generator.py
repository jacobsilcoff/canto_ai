import asyncio
import json
import os
import time
import re  # Added for punctuation check
from openai import OpenAI
import edge_tts
from dotenv import load_dotenv
from jyutping_utils import get_accurate_jyutping

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/units")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets/audio")
VOCAB_PATH = os.path.join(os.path.dirname(__file__), "../data/vocab.json")

# ... SYSTEM_PROMPT ... (Keep your existing prompt from the previous step)
SYSTEM_PROMPT = """
You are a Mango-style Cantonese course architect. Create ONE learning Unit based on the user's topic.

LINGUISTIC STYLE:
- Natural, spoken Hong Kong Cantonese (Colloquial).
- Beginner to low-intermediate difficulty.
- NO Jyutping in output (backend handles it).
- Use sentence-final particles naturally and frequently.

CONVERSATION RULES:
- Length: 6 to 8 turns (sentences).
- ONE sentence per turn.
- Speakers must alternate: A, B, A, B...
- The conversation should be realistic, instructional, and build context.

CHUNKING RULES (CRITICAL):
- Chunks must be the smallest reusable grammatical units.
- Numerals MUST be separate chunks (e.g., "一").
- Classifiers MUST be separate chunks (e.g., "杯").
- Nouns MUST be separate chunks (e.g., "咖啡").
- Verbs and aspect markers MUST be separate chunks (e.g., "要", "咗").
- Sentence-final particles MUST be their own chunks (e.g., "呀", "呢", "喇").
- Do NOT combine multiple grammatical functions into one chunk.
- Every character in the Cantonese sentence must appear in exactly ONE chunk.
- Chunks must appear verbatim and in order.

PARTICLE MEANING RULE (CRITICAL):
- For sentence-final particles (呀 / 呢 / 喇 / 啦 / 啊 etc.), the English explanation MUST describe the particle’s pragmatic function.
- Enclose the explanation in parentheses.
- Example: "(softens the tone)", "(seeking confirmation)", "(indicates change of state)".
- Do NOT label it as "particle".

OUTPUT FORMAT:
- Output VALID JSON ONLY.
- No text outside JSON.
- Follow this schema exactly:
{
  "title": "Topic Title",
  "topic_description": "Short description",
  "conversation": [
    {
      "id": 0,
      "speaker": "A",
      "cantonese": "Cantonese text here",
      "english_natural": "Natural fluent English translation",
      "chunks": [
        { "cantonese": "word", "english": "meaning" },
        { "cantonese": "particle", "english": "(pragmatic function)" }
      ]
    }
  ]
}
"""


async def generate_audio_file(text, filepath, voice):
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filepath)
    except Exception as e:
        print(f"Error generating audio {filepath}: {e}")


def update_global_vocab(chunks):
    """
    Updates vocab.json, filtering out punctuation.
    """
    if not os.path.exists(VOCAB_PATH):
        vocab_list = []
    else:
        with open(VOCAB_PATH, 'r', encoding='utf-8') as f:
            vocab_list = json.load(f)

    existing_words = {item['cantonese'] for item in vocab_list}

    # Regex to identify "pure punctuation" chunks (e.g., "?", "。", "！")
    punct_pattern = re.compile(r'^[^\w\s\u4e00-\u9fff]+$')

    for chunk in chunks:
        canto = chunk['cantonese']

        # SKIP if it exists OR if it matches punctuation pattern
        if canto in existing_words or punct_pattern.match(canto):
            continue

        vocab_list.append({
            "cantonese": canto,
            "jyutping": chunk['jyutping'],
            "english": chunk['english'],
            "learned_date": time.time(),
            "next_review": time.time(),
            "interval": 0,
            "reps": 0
        })

    with open(VOCAB_PATH, 'w', encoding='utf-8') as f:
        json.dump(vocab_list, f, ensure_ascii=False, indent=2)


# ... build_unit function stays the same as previous response ...
async def build_unit(topic):
    unit_id = str(int(time.time()))
    unit_audio_dir = os.path.join(ASSETS_DIR, unit_id)
    os.makedirs(unit_audio_dir, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"Designing Unit: {topic}...")
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}"}
        ]
    )
    unit_data = json.loads(response.choices[0].message.content)
    unit_data['id'] = unit_id
    if len(unit_data['title']) > 50: unit_data['title'] = topic

    tasks = []
    all_chunks = []

    print("Synthesizing Audio...")
    for s_idx, sentence in enumerate(unit_data['conversation']):
        sentence['jyutping'] = get_accurate_jyutping(sentence['cantonese'])

        # Sentence Audio
        s_filename = f"sent_{s_idx}.mp3"
        s_path = os.path.join(unit_audio_dir, s_filename)
        sentence['audio_rel_path'] = f"{unit_id}/{s_filename}"

        voice = "zh-HK-HiuGaaiNeural" if sentence['speaker'] == "A" else "zh-HK-WanLungNeural"
        tasks.append(generate_audio_file(sentence['cantonese'], s_path, voice))

        # Chunk Audio
        for c_idx, chunk in enumerate(sentence['chunks']):
            chunk['jyutping'] = get_accurate_jyutping(chunk['cantonese'])
            c_filename = f"chunk_{s_idx}_{c_idx}.mp3"
            c_path = os.path.join(unit_audio_dir, c_filename)
            chunk['audio_rel_path'] = f"{unit_id}/{c_filename}"
            tasks.append(generate_audio_file(chunk['cantonese'], c_path, voice))
            all_chunks.append(chunk)

    await asyncio.gather(*tasks)
    update_global_vocab(all_chunks)

    with open(os.path.join(DATA_DIR, f"{unit_id}.json"), 'w', encoding='utf-8') as f:
        json.dump(unit_data, f, ensure_ascii=False, indent=2)

    print(f"Unit '{unit_data['title']}' created successfully.")
    return unit_data