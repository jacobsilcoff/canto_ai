"""
Lesson Page
Renders the interactive lesson player
"""
import streamlit as st
from core.state import navigate_to, get_state, set_state
from services.lesson_service import generate_lesson_plan
from services.progress_service import save_lesson_progress
from components.player import render_player

def render():
    """Render lesson player"""
    unit = get_state('current_unit')
    lesson_range = get_state('lesson_range')
    lesson_key = get_state('lesson_key')
    lesson_type = get_state('lesson_type', 'full')

    if not unit or not lesson_range:
        st.error("No lesson selected")
        if st.button("← Back"):
            navigate_to('dashboard')
            st.rerun()
        return

    unit_id = unit.get('id')

    # Check query params for completion
    query_params = st.query_params
    if query_params.get('completed') == 'true':
        save_lesson_progress(unit_id, lesson_key, completed=True)
        st.success("✅ Lesson completed! Great job! 🎉")
        st.balloons()
        if st.button("📚 Back to Unit", type="primary"):
            st.query_params.clear()
            navigate_to('dashboard', current_unit=unit)
            st.rerun()
        return

    # Header with back button only
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title(unit.get('title', 'Lesson'))
    with col2:
        if st.button("← Back"):
            navigate_to('dashboard', current_unit=unit)
            st.rerun()

    # Generate and render lesson
    start, end = lesson_range
    subset = unit['conversation'][start:end]
    lesson_plan = generate_lesson_plan(subset, lesson_type)

    render_player(lesson_plan, key=lesson_key, srs_mode=False)