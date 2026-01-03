"""
Library Page
Displays and manages learning units
"""
import asyncio
import streamlit as st
from core.state import navigate_to
from services.unit_service import get_all_units, load_unit
from services.srs_service import get_vocab_stats
from generators.content_generator import build_unit

def render_sidebar_create():
    """Render unit creation in sidebar"""
    st.subheader("✨ Create New Unit")

    topic = st.text_input(
        "Topic",
        placeholder="e.g., Ordering food at a restaurant",
        help="What situation or topic would you like to learn?"
    )

    if st.button("🚀 Generate Unit", type="primary", use_container_width=True):
        if topic.strip():
            with st.spinner("Creating your lesson... 🎨"):
                asyncio.run(build_unit(topic.strip()))
            st.success("✅ Unit created!")
            st.rerun()
        else:
            st.error("Please enter a topic")

    st.markdown("---")

    # Stats
    stats = get_vocab_stats()
    st.metric("📚 Total Words", stats['total'])
    if stats['due'] > 0:
        st.metric("🔔 Due for Review", stats['due'])

def render():
    """Render main library view"""
    st.title("📚 Your Learning Library")
    st.markdown("Select a unit to start learning or create a new one in the sidebar.")

    units = get_all_units()

    if not units:
        st.info("""
        👋 Welcome! You don't have any units yet.
        
        **Get started:**
        1. Enter a topic in the sidebar
        2. Click "Generate Unit"
        3. Start learning!
        
        Try topics like:
        - Ordering at a café
        - Meeting new people
        - Asking for directions
        """)
        return

    # Display units in a grid
    cols_per_row = 2
    for i in range(0, len(units), cols_per_row):
        cols = st.columns(cols_per_row)

        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(units):
                break

            unit_file = units[idx]
            unit = load_unit(unit_file)

            if not unit:
                continue

            with col:
                _render_unit_card(unit, unit_file)

def _render_unit_card(unit: dict, filename: str):
    """Render a single unit card"""
    from services.progress_service import get_unit_completion_stats
    from core.constants import LESSON_CHUNK_SIZE

    # Calculate progress
    conversation = unit.get('conversation', [])
    total_lessons = (len(conversation) + LESSON_CHUNK_SIZE - 1) // LESSON_CHUNK_SIZE
    unit_id = unit.get('id')
    stats = get_unit_completion_stats(unit_id, total_lessons)

    progress_text = ""
    if stats['completed'] > 0:
        progress_text = f"<div style='margin-top: 10px; color: #10b981; font-weight: 600; font-size: 0.85em;'>✓ {stats['completed']}/{stats['total']} lessons completed</div>"

    with st.container():
        st.markdown(f"""
        <div style="
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            background: white;
            height: 100%;
        ">
            <h3 style="margin: 0 0 10px 0; color: #1f2937;">
                {unit.get('title', 'Untitled')}
            </h3>
            <p style="color: #6b7280; margin-bottom: 15px; font-size: 0.9em;">
                {unit.get('topic_description', 'No description')}
            </p>
            <div style="color: #9ca3af; font-size: 0.85em;">
                📝 {len(unit.get('conversation', []))} sentences
            </div>
            {progress_text}
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("📖 Open", key=f"open_{filename}", use_container_width=True):
                navigate_to('dashboard', current_unit=unit)
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{filename}", help="Delete unit"):
                st.session_state[f'confirm_delete_{filename}'] = True
                st.rerun()

        # Confirm deletion
        if st.session_state.get(f'confirm_delete_{filename}', False):
            st.warning("⚠️ Delete this unit?")
            c1, c2 = st.columns(2)
            if c1.button("Yes", key=f"yes_{filename}"):
                from services.unit_service import delete_unit
                delete_unit(filename)
                st.session_state[f'confirm_delete_{filename}'] = False
                st.rerun()
            if c2.button("No", key=f"no_{filename}"):
                st.session_state[f'confirm_delete_{filename}'] = False
                st.rerun()

        st.markdown("---")