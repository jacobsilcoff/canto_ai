"""
Mango-Style Cantonese Learning App
Main entry point - handles routing only
"""
import streamlit as st
from core.state import init_session_state
from pages import library, dashboard, lesson, review

st.set_page_config(
    layout="wide",
    page_title="🥭 Canto Learn",
    page_icon="🥭",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Sidebar navigation
with st.sidebar:
    st.title("🥭 Canto Learn")
    st.markdown("---")

    # Show navigation based on current view
    if st.session_state.view == 'library':
        # Library view - show review button and creation
        if st.button("🧠 Review", use_container_width=True, type="secondary"):
            st.session_state.view = 'review'
            st.rerun()
        st.markdown("---")
        library.render_sidebar_create()

    elif st.session_state.view == 'review':
        # Review view - show library button and stats
        if st.button("📚 Library", use_container_width=True, type="secondary"):
            st.session_state.view = 'library'
            st.rerun()
        st.markdown("---")
        from services.srs_service import get_vocab_stats
        stats = get_vocab_stats()
        st.metric("📚 Total Words", stats['total'])
        st.metric("✅ Learned", stats['learned'])
        st.metric("🔔 Due Today", stats['due'])

    elif st.session_state.view == 'dashboard':
        # Dashboard view - show library button
        if st.button("📚 Library", use_container_width=True, type="secondary"):
            st.session_state.view = 'library'
            st.rerun()
        st.markdown("---")
        # Show unit info
        unit = st.session_state.get('current_unit')
        if unit:
            st.subheader("Current Unit")
            st.write(unit.get('title', 'Untitled'))

    elif st.session_state.view == 'lesson':
        # Lesson view - show useful emoji buttons
        if st.button("📚 Library", use_container_width=True):
            st.session_state.view = 'library'
            st.rerun()
        if st.button("🧠 Review", use_container_width=True):
            st.session_state.view = 'review'
            st.rerun()
        st.markdown("---")
        unit = st.session_state.get('current_unit')
        if unit:
            st.info(f"📖 {unit.get('title', 'Lesson')}")

# Main content routing
if st.session_state.view == 'library':
    library.render()
elif st.session_state.view == 'dashboard':
    dashboard.render()
elif st.session_state.view == 'lesson':
    lesson.render()
elif st.session_state.view == 'review':
    review.render()