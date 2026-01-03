import asyncio
import streamlit as st
import data_manager
import srs_engine
from components import render_mango_player
from generator import build_unit

st.set_page_config(layout="wide", page_title="Mango-Style Canto")

if 'view' not in st.session_state: st.session_state['view'] = 'library'
if 'current_unit' not in st.session_state: st.session_state['current_unit'] = None
if 'lesson_range' not in st.session_state: st.session_state['lesson_range'] = None
if 'lesson_key' not in st.session_state: st.session_state['lesson_key'] = None
if 'srs_queue' not in st.session_state: st.session_state['srs_queue'] = []

COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#6366f1"]


def nav_to(view_name): st.session_state['view'] = view_name


def open_unit(unit_data):
    st.session_state['current_unit'] = unit_data
    st.session_state['view'] = 'dashboard'


def start_lesson_session(unit, start, end, lesson_key):
    st.session_state['current_unit'] = unit
    st.session_state['lesson_range'] = (start, end)
    st.session_state['lesson_key'] = lesson_key
    st.session_state['view'] = 'player'


def generate_smart_lesson_plan(subset):
    slides = []

    # 1. Intro
    intro_subset = []
    for sent in subset:
        sent_copy = sent.copy()
        enriched_chunks = []
        for c_idx, chunk in enumerate(sent['chunks']):
            chunk_copy = chunk.copy()
            chunk_copy['color'] = COLORS[c_idx % len(COLORS)]
            enriched_chunks.append(chunk_copy)
        sent_copy['chunks'] = enriched_chunks
        intro_subset.append(sent_copy)
    slides.append({"type": "intro_dialogue", "data": intro_subset})

    # 2. Build-up
    for sent in subset:
        enriched_chunks = []
        for c_idx, chunk in enumerate(sent['chunks']):
            chunk_copy = chunk.copy()
            chunk_copy['color'] = COLORS[c_idx % len(COLORS)]
            enriched_chunks.append(chunk_copy)

        analysis_data = sent.copy()
        analysis_data['chunks'] = enriched_chunks
        slides.append({"type": "analysis", "data": analysis_data})

        history = []
        for chunk in enriched_chunks:
            if chunk['cantonese'] in ["。", "，", "？", "！", ".", ",", "?", "!"]:
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

        slides.append({
            "type": "quiz_recall",
            "target_chunks": enriched_chunks,
            "target_english": sent['english_natural'],
            "target_audio": sent['audio_rel_path'],
            "context": [],
            "mode": "sentence"
        })

    return slides


with st.sidebar:
    st.title("🥭 Canto Clone")
    if st.button("📚 Library", use_container_width=True): nav_to('library'); st.rerun()
    if st.button("🧠 Review (SRS)", use_container_width=True): nav_to('srs'); st.rerun()
    st.divider()
    if st.session_state['view'] == 'library':
        topic = st.text_input("New Unit Topic")
        if st.button("Create Unit", type="primary"):
            if topic:
                with st.spinner("Creating unit..."): asyncio.run(build_unit(topic))
                st.rerun()

if st.session_state['view'] == 'library':
    st.header("📚 Your Units")
    files = data_manager.get_all_units()
    if not files: st.info("No units yet. Create one in the sidebar!")

    for f in files:
        try:
            u = data_manager.load_unit(f)
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(u.get('title', 'Untitled'))
                st.caption(u.get('topic_description', ''))
            with c2:
                st.button("Open", key=f, on_click=open_unit, args=(u,))
            st.divider()
        except:
            pass

elif st.session_state['view'] == 'dashboard':
    if st.button("⬅️ Back"): nav_to('library'); st.rerun()
    unit = st.session_state['current_unit']
    st.title(unit.get('title'))

    st.button("👂 Listen to Full Conversation", use_container_width=True,
              on_click=start_lesson_session,
              args=(unit, 0, len(unit['conversation']), "full_conv"))

    st.subheader("Lessons")
    CHUNK_SIZE = 1
    for i in range(0, len(unit['conversation']), CHUNK_SIZE):
        batch_end = min(i + CHUNK_SIZE, len(unit['conversation']))
        lesson_num = (i // CHUNK_SIZE) + 1
        lesson_key = f"lesson_{lesson_num}"
        c1, c2 = st.columns([4, 1])
        with c1: st.markdown(f"**Lesson {lesson_num}**")
        with c2: st.button(f"Start", key=lesson_key, on_click=start_lesson_session,
                           args=(unit, i, batch_end, lesson_key))
        st.divider()

elif st.session_state['view'] == 'player':
    unit = st.session_state['current_unit']
    start, end = st.session_state['lesson_range']
    subset = unit['conversation'][start:end]
    lesson_plan = generate_smart_lesson_plan(subset)
    if st.button("❌ Exit Lesson"): nav_to('dashboard'); st.rerun()
    render_mango_player(lesson_plan, key=st.session_state['lesson_key'])

# --- SRS MODE ---
elif st.session_state['view'] == 'srs':
    st.header("🧠 Review Mode")
    if not st.session_state['srs_queue']:
        st.session_state['srs_queue'] = srs_engine.get_due_cards()

    queue = st.session_state['srs_queue']
    if not queue:
        st.success("🎉 All caught up!")
        if st.button("Back to Library"): nav_to('library'); st.rerun()
    else:
        card = queue[0]

        # Robust construction: keys default to None if missing
        srs_slide = {
            "type": "quiz_recall",
            "target_chunks": [{
                "cantonese": card.get('cantonese'),
                "jyutping": card.get('jyutping'),
                "english": card.get('english'),
                "audio_rel_path": card.get('audio_rel_path'),
                "color": COLORS[0]
            }],
            "target_english": card.get('english'),
            "target_audio": card.get('audio_rel_path'),
            "context": [],
            "mode": "chunk"
        }

        render_mango_player([srs_slide], key=f"srs_{card['cantonese']}", srs_mode=True)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)


        def handle_srs(quality):
            srs_engine.update_card(card['cantonese'], quality)
            st.session_state['srs_queue'].pop(0)


        if c1.button("Wrong / Forgot", use_container_width=True):
            handle_srs(0)
            st.rerun()
        if c2.button("Good", use_container_width=True):
            handle_srs(3)
            st.rerun()
        if c3.button("Easy", use_container_width=True):
            handle_srs(5)
            st.rerun()