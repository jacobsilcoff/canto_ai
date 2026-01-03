"""
Application Constants and Configuration
"""
import os

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "units")
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
VOCAB_PATH = os.path.join(BASE_DIR, "data", "vocab.json")
PROGRESS_PATH = os.path.join(BASE_DIR, "data", "progress.json")

# UI Colors - Modern, vibrant palette
COLORS = {
    'primary': '#3b82f6',      # Blue
    'success': '#10b981',      # Green
    'warning': '#f59e0b',      # Amber
    'purple': '#8b5cf6',       # Purple
    'pink': '#ec4899',         # Pink
    'indigo': '#6366f1',       # Indigo
}

CHUNK_COLORS = list(COLORS.values())

# TTS Voices
VOICES = {
    'A': 'zh-HK-HiuGaaiNeural',  # Female voice
    'B': 'zh-HK-WanLungNeural',  # Male voice
}

# Learning Settings
LESSON_CHUNK_SIZE = 1  # Sentences per lesson
SRS_INTERVALS = {
    'wrong': 1,      # 1 day
    'good': 1.5,     # Multiplier
    'easy': 2.0,     # Multiplier
}

# UI Settings
PLAYER_HEIGHT = 850
PLAYER_HEIGHT_SRS = 550
SIDEBAR_WIDTH = 300

# Punctuation (exclude from vocab)
PUNCTUATION = {'。', '，', '？', '！', '.', ',', '?', '!', '；', '：', ';', ':'}