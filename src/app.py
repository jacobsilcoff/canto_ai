import asyncio
import streamlit as st
import data_manager
import srs_engine
from components import render_mango_player
from generator import build_unit

st.set_page_config(layout="wide", page_title="Mango-Style Canto")

# --- INITIALIZATION ---
if 'view' not in st.session_state: st.session_state['view'] = 'library'
if 'current_unit' not in st.session_state: st.session_state['current_unit'] = None
if 'lesson_range' not in st.session_state: st.session_state['lesson_range'] = None
if 'lesson_key' not in st.session_state: st.session_state['lesson_key'] = None
if 'slide_idx' not in st.session_state: st.session_state['slide_idx'] = 0
if 'srs_queue' not in st.session_state: st.session_state['srs_queue'] = []
if 'srs_revealed' not in st.session_state: st.session_state['srs_revealed'] = False


# --- CONTROLLER FUNCTIONS ---
def nav_to(view_name):
    st.session_state['view'] = view_name


def open_unit(unit_data):
    st.session_state['current_unit'] = unit_data
    st.session_state['view'] = 'dashboard'


def start_lesson_session(unit, start, end, lesson_key):
    st.session_state['current_unit'] = unit
    st.session_state['lesson_range'] = (start, end)
    st.session_state['lesson_key'] = lesson_key
    saved_idx = data_manager.get_progress(unit['id'], lesson_key)
    st.session_state['slide_idx'] = saved_idx
    st.session_state['view'] = 'player'


def next_slide():
    st.session_state['slide_idx'] += 1
    data_manager.save_progress(st.session_state['current_unit']['id'],
                               st.session_state['lesson_key'],
                               st.session_state['slide_idx'])


def prev_slide():
    st.session_state['slide_idx'] -= 1
    data_manager.save_progress(st.session_state['current_unit']['id'],
                               st.session_state['lesson_key'],
                               st.session_state['slide_idx'])


# --- SIDEBAR ---
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

# --- MAIN VIEWS ---

# 1. LIBRARY
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

# 2. DASHBOARD
elif st.session_state['view'] == 'dashboard':
    if st.button("⬅️ Back"): nav_to('library'); st.rerun()
    unit = st.session_state['current_unit']
    st.title(unit.get('title'))

    st.button("👂 Listen to Full Conversation", use_container_width=True,
              on_click=start_lesson_session,
              args=(unit, 0, len(unit['conversation']), "full_conv"))

    st.subheader("Lessons")
    CHUNK_SIZE = 2
    for i in range(0, len(unit['conversation']), CHUNK_SIZE):
        batch_end = min(i + CHUNK_SIZE, len(unit['conversation']))
        lesson_num = (i // CHUNK_SIZE) + 1
        lesson_key = f"lesson_{lesson_num}"
        saved_idx = data_manager.get_progress(unit['id'], lesson_key)
        prog_text = f" • Resume at Slide {saved_idx + 1}" if saved_idx > 0 else ""

        c1, c2 = st.columns([4, 1])
        with c1: st.markdown(f"**Lesson {lesson_num}**{prog_text}")
        with c2: st.button(f"Start L{lesson_num}", key=lesson_key, on_click=start_lesson_session,
                           args=(unit, i, batch_end, lesson_key))
        st.divider()

# 3. PLAYER
elif st.session_state['view'] == 'player':
    unit = st.session_state['current_unit']
    start, end = st.session_state['lesson_range']
    subset = unit['conversation'][start:end]

    slides = []
    slides.append({"type": "intro_dialogue", "data": subset})
    for sent in subset:
        slides.append({"type": "analysis", "data": sent})
        history = []
        for chunk in sent['chunks']:
            history.append(chunk)
            slides.append({"type": "quiz_recall", "target_chunk": chunk, "context": list(history[:-1])})
    slides.append({"type": "intro_dialogue", "data": subset})

    curr = st.session_state['slide_idx']
    st.progress((curr + 1) / len(slides))
    if st.button("Exit Lesson"): nav_to('dashboard'); st.rerun()

    render_mango_player(slides[curr], key=f"slide_{curr}")

    c1, c2 = st.columns([1, 1])
    with c1:
        if curr > 0: st.button("Prev", use_container_width=True, on_click=prev_slide)
    with c2:
        if curr < len(slides) - 1:
            st.button("Next", use_container_width=True, on_click=next_slide)
        else:
            if st.button("Finish", type="primary", use_container_width=True):
                data_manager.save_progress(unit['id'], st.session_state['lesson_key'], 0)
                nav_to('dashboard');
                st.rerun()

# 4. SRS (Review)
elif st.session_state['view'] == 'srs':
    st.header("🧠 Review Mode")
    if not st.session_state['srs_queue']:
        st.session_state['srs_queue'] = srs_engine.get_due_cards()

    queue = st.session_state['srs_queue']
    if not queue:
        st.success("🎉 All caught up!")
    else:
        card = queue[0]
        with st.container(border=True):
            st.markdown(f"<h3 style='text-align:center'>{card['english']}</h3>", unsafe_allow_html=True)
            if st.session_state['srs_revealed']:
                st.divider()
                st.markdown(f"<h1 style='text-align:center; color:#2563eb'>{card['cantonese']}</h1>",
                            unsafe_allow_html=True)
                st.markdown(f"<p style='text-align:center; color:gray'>{card['jyutping']}</p>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)


                def handle_srs(quality):
                    srs_engine.update_card(card['cantonese'], quality)
                    st.session_state['srs_queue'].pop(0)
                    st.session_state['srs_revealed'] = False


                if c1.button("Wrong"): handle_srs(0); st.rerun()
                if c2.button("Good"): handle_srs(3); st.rerun()
                if c3.button("Easy"): handle_srs(5); st.rerun()
            else:
                if st.button("Show Answer"): st.session_state['srs_revealed'] = True; st.rerun()