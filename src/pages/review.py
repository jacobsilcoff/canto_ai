"""
Review Page
Spaced repetition review system
"""
import streamlit as st
from core.state import navigate_to, get_state, set_state
from services.srs_service import get_due_cards, update_card, get_vocab_stats
from services.lesson_service import create_srs_slide
from components.player import render_player


def render():
    """Render SRS review interface"""
    st.title("🧠 Review Mode")
    st.markdown("Practice words you've learned using spaced repetition.")

    # Initialize queue if empty
    if not get_state('srs_queue'):
        set_state('srs_queue', get_due_cards())

    queue = get_state('srs_queue', [])
    stats = get_vocab_stats()

    # Show stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total Words", stats['total'])
    with col2:
        st.metric("✅ Learned", stats['learned'])
    with col3:
        st.metric("🔔 Remaining Today", len(queue))

    st.markdown("---")

    # No cards due
    if not queue:
        st.success("🎉 All caught up! Great work!")
        st.markdown("""
        **You've reviewed all your cards for today.**

        - Come back tomorrow for more practice
        - Or create new units to learn more words
        """)

        if st.button("📚 Back to Library", type="primary"):
            navigate_to('library')
            st.rerun()
        return

    # Show current card
    card = queue[0]
    slide = create_srs_slide(card)

    # Render the quiz
    render_player([slide], key=f"srs_{card['cantonese']}", srs_mode=True)

    # Quality buttons
    st.markdown("---")
    st.markdown("### How well did you know this word?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("❌ Again", use_container_width=True, help="I didn't remember"):
            _handle_response(card, 0)
            st.rerun()

    with col2:
        if st.button("✅ Good", use_container_width=True, help="I remembered with some effort"):
            _handle_response(card, 3)
            st.rerun()

    with col3:
        if st.button("🎯 Easy", use_container_width=True, help="I remembered instantly"):
            _handle_response(card, 5)
            st.rerun()

    # Progress indicator
    progress = (stats['total'] - len(queue)) / max(stats['total'], 1)
    st.progress(progress)
    st.caption(f"Progress: {stats['total'] - len(queue)}/{stats['total']} words reviewed today")


def _handle_response(card: dict, quality: int):
    """Handle user response to review card"""
    update_card(card['cantonese'], quality)

    # Remove from queue
    queue = get_state('srs_queue', [])
    if queue:
        queue.pop(0)
        set_state('srs_queue', queue)