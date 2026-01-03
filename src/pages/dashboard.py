"""
Dashboard Page
Shows unit details and lesson selection
"""
import streamlit as st
from core.state import navigate_to, get_state
from core.constants import LESSON_CHUNK_SIZE
from services.progress_service import get_unit_completion_stats, get_lesson_progress, mark_lesson_started

def render():
    """Render unit dashboard"""
    unit = get_state('current_unit')

    if not unit:
        st.error("No unit selected")
        if st.button("← Back to Library"):
            navigate_to('library')
            st.rerun()
        return

    unit_id = unit.get('id')
    conversation = unit.get('conversation', [])
    total_lessons = (len(conversation) + LESSON_CHUNK_SIZE - 1) // LESSON_CHUNK_SIZE

    # Get progress stats
    stats = get_unit_completion_stats(unit_id, total_lessons)

    # Header
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title(unit.get('title', 'Untitled Unit'))
        st.markdown(f"*{unit.get('topic_description', '')}*")
    with col2:
        if st.button("← Back"):
            navigate_to('library')
            st.rerun()

    # Progress bar
    if stats['completed'] > 0:
        st.progress(stats['percentage'] / 100)
        st.caption(f"Progress: {stats['completed']}/{stats['total']} lessons completed ({stats['percentage']:.0f}%)")

    st.markdown("---")

    # Quick start - full conversation
    st.subheader("🎧 Quick Listen")
    st.markdown("Listen to the full conversation to get familiar with the content.")

    if st.button(
        "▶️ Play Full Conversation",
        use_container_width=True,
        type="primary"
    ):
        _start_lesson(
            unit=unit,
            start=0,
            end=len(unit['conversation']),
            lesson_key="full_conv",
            lesson_type='quick'
        )
        st.rerun()

    st.markdown("---")

    # Lesson breakdown
    st.subheader("📚 Lessons")
    st.markdown("Each lesson focuses on a small part of the conversation.")

    conversation = unit.get('conversation', [])
    total_lessons = (len(conversation) + LESSON_CHUNK_SIZE - 1) // LESSON_CHUNK_SIZE

    # Display lessons in a grid
    cols = st.columns(3)
    for i in range(0, len(conversation), LESSON_CHUNK_SIZE):
        batch_end = min(i + LESSON_CHUNK_SIZE, len(conversation))
        lesson_num = (i // LESSON_CHUNK_SIZE) + 1
        lesson_key = f"lesson_{lesson_num}"

        col_idx = ((lesson_num - 1) % 3)

        with cols[col_idx]:
            _render_lesson_card(
                lesson_num=lesson_num,
                start=i,
                end=batch_end,
                lesson_key=lesson_key,
                unit=unit,
                conversation=conversation
            )

def _render_lesson_card(lesson_num, start, end, lesson_key, unit, conversation):
    """Render a lesson card"""
    preview = conversation[start].get('cantonese', '')[:20] + "..."

    # Check if completed
    unit_id = unit.get('id')
    progress = get_lesson_progress(unit_id, lesson_key)
    is_completed = progress.get('completed', False)

    status_badge = "✅" if is_completed else "◯"
    border_color = "#10b981" if is_completed else "#e5e7eb"

    st.markdown(f"""
    <div style="
        padding: 15px;
        border-radius: 10px;
        border: 2px solid {border_color};
        background: white;
        margin-bottom: 10px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
            <div style="font-weight: bold; color: #3b82f6; font-size: 1.1em;">
                Lesson {lesson_num}
            </div>
            <div style="font-size: 1.5em;">
                {status_badge}
            </div>
        </div>
        <div style="color: #6b7280; font-size: 0.85em; margin-bottom: 10px;">
            {preview}
        </div>
        <div style="color: #9ca3af; font-size: 0.75em;">
            {end - start} sentence(s)
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_text = "▶️ Review" if is_completed else "▶️ Start"

    if st.button(
        btn_text,
        key=lesson_key,
        use_container_width=True,
        type="secondary"
    ):
        mark_lesson_started(unit_id, lesson_key)
        _start_lesson(unit, start, end, lesson_key, 'full')
        st.rerun()

def _start_lesson(unit, start, end, lesson_key, lesson_type='full'):
    """Navigate to lesson with parameters"""
    navigate_to(
        'lesson',
        current_unit=unit,
        lesson_range=(start, end),
        lesson_key=lesson_key,
        lesson_type=lesson_type
    )