# 🥭 Mango-Style Cantonese Learning App

A modern, interactive Cantonese learning application inspired by Mango Languages, featuring AI-generated content, spaced repetition, and immersive dialogue practice.

## ✨ Features

- **AI-Powered Content Generation**: Create custom learning units on any topic
- **Interactive Lesson Player**: Mango-style interface with chunked vocabulary
- **Spaced Repetition System**: Smart review scheduling for long-term retention
- **Natural TTS Audio**: High-quality Cantonese pronunciation for every word
- **Jyutping Support**: Automatic romanization for pronunciation guidance
- **Modern UI**: Dark mode support, smooth animations, responsive design

## 📁 Project Structure

```
/
├── app.py                          # Main entry point & routing
├── core/
│   ├── state.py                    # Session state management
│   └── constants.py                # Configuration & constants
├── pages/
│   ├── library.py                  # Library view (unit listing)
│   ├── dashboard.py                # Unit dashboard (lesson selection)
│   ├── lesson.py                   # Lesson player view
│   └── review.py                   # SRS review interface
├── services/
│   ├── unit_service.py             # Unit CRUD operations
│   ├── lesson_service.py           # Lesson plan generation
│   └── srs_service.py              # Spaced repetition logic
├── components/
│   ├── player.py                   # Main player component
│   ├── player_styles.py            # CSS styles for player
│   └── player_javascript.py        # JavaScript for player
├── generators/
│   ├── content_generator.py        # AI content generation
│   └── audio_generator.py          # TTS audio generation
└── utils/
    ├── audio.py                    # Audio encoding utilities
    └── jyutping.py                 # Jyutping conversion
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install streamlit openai edge-tts pycantonese python-dotenv
```

### Environment Setup

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
```

### Run the App

```bash
streamlit run app.py
```

## 📚 Usage Guide

### Creating a Unit

1. Enter a topic in the sidebar (e.g., "Ordering at a restaurant")
2. Click "Generate Unit"
3. Wait for AI to create the conversation and audio
4. Unit appears in your library

### Learning a Lesson

1. Open a unit from the library
2. Choose "Quick Listen" to hear the full conversation
3. Or start individual lessons for detailed practice
4. Each lesson includes:
   - Full dialogue introduction
   - Sentence-by-sentence breakdown
   - Chunk-level vocabulary practice
   - Recording and comparison tools

### Reviewing Vocabulary

1. Click "Review" in the sidebar
2. Practice words using spaced repetition
3. Rate your recall: Again / Good / Easy
4. Words automatically scheduled for optimal review

## 🎨 UI/UX Design Principles

### Modern & Clean
- Minimalist interface with focus on content
- Smooth animations and transitions
- Consistent color scheme with semantic meaning

### Mango-Inspired Features
- Chunked vocabulary display
- Color-coded grammatical units
- Interactive hover effects
- Natural dialogue flow

### Accessibility
- Dark mode support
- High contrast ratios
- Clear visual hierarchy
- Responsive design for mobile

## 🔧 Architecture Highlights

### Modular Design
Each module has a single, clear responsibility:
- **Pages**: UI rendering only
- **Services**: Business logic
- **Generators**: Content creation
- **Utils**: Reusable helpers

### LLM-Friendly Structure
- Small, focused files (< 200 lines)
- Clear function signatures
- Descriptive naming
- Minimal cross-dependencies

### State Management
Centralized in `core/state.py`:
- Predictable state updates
- Easy debugging
- Type-safe helpers

## 🎯 Design Philosophy

### For Users
1. **Natural Learning**: Focus on realistic conversations
2. **Immediate Feedback**: Audio playback and visual cues
3. **Incremental Progress**: Small, manageable lessons
4. **Effective Review**: SRS for long-term retention

### For Developers
1. **Easy to Understand**: Clear module boundaries
2. **Easy to Modify**: Change one thing at a time
3. **Easy to Extend**: Add new features without refactoring
4. **AI-Friendly**: Perfect for LLM-assisted development

## 📝 Key Concepts

### Units
A unit is a complete learning module with:
- A topic/situation
- 6-8 sentence conversation
- Chunked vocabulary
- Audio for every element

### Chunks
Smallest grammatical units:
- Individual characters/words
- Particles (with pragmatic meanings)
- Color-coded for visual grouping
- Clickable for audio playback

### Slides
A lesson is composed of slides:
- **intro_dialogue**: Full conversation overview
- **analysis**: Sentence breakdown
- **quiz_recall**: Practice and recall

### SRS (Spaced Repetition)
Algorithm for optimal review scheduling:
- **Wrong** (0): Reset to 1 day
- **Good** (3): Multiply interval by 1.5
- **Easy** (5): Multiply interval by 2.0

## 🛠️ Development Tips

### Adding a New Page
1. Create file in `pages/`
2. Add `render()` function
3. Import in `app.py`
4. Add navigation button

### Modifying the Player
- **Styles**: Edit `components/player_styles.py`
- **Logic**: Edit `components/player_javascript.py`
- **Data processing**: Edit `components/player.py`

### Changing AI Prompts
Edit `SYSTEM_PROMPT` in `generators/content_generator.py`

### Adding New TTS Voices
Add to `VOICES` dict in `core/constants.py`

## 🐛 Troubleshooting

### Audio Not Playing
- Check `assets/audio/` directory exists
- Verify audio files were generated
- Check browser console for errors

### Units Not Saving
- Check `data/units/` directory permissions
- Verify OpenAI API key is valid
- Check console for error messages

### Jyutping Errors
- Ensure `pycantonese` is installed
- Some characters may not have entries
- Check input is valid Cantonese

## 📊 Performance Considerations

- Audio files are base64 encoded for embedding
- Parallel TTS generation for faster unit creation
- Minimal re-renders using Streamlit best practices
- Vocabulary filtering to avoid duplicate entries

## 🔜 Future Enhancements

- [ ] Progress tracking and statistics
- [ ] Multiple difficulty levels
- [ ] Grammar explanations
- [ ] Writing practice mode
- [ ] Export/import units
- [ ] Collaborative learning features

## 📄 License

This is a learning project. Modify and use as you wish!

## 🙏 Acknowledgments

- Inspired by Mango Languages
- Built with Streamlit
- Powered by OpenAI GPT-4
- TTS by Microsoft Edge
- Jyutping by PyCantonese

---

Made with ❤️ for Cantonese learners