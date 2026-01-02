import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../data/units")
AUDIO_BASE = os.path.join(BASE_DIR, "../assets/audio")
VOCAB_PATH = os.path.join(BASE_DIR, "../data/vocab.json")
PROGRESS_PATH = os.path.join(BASE_DIR, "../data/progress.json")