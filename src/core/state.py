"""
Session State Management
Centralized state initialization and helpers
"""
import streamlit as st


def init_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'view': 'library',
        'current_unit': None,
        'lesson_range': None,
        'lesson_key': None,
        'srs_queue': [],
        'audio_autoplay': True,
        'show_jyutping': False,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def navigate_to(view_name: str, **kwargs):
    """Navigate to a different view with optional parameters"""
    st.session_state.view = view_name
    for key, value in kwargs.items():
        st.session_state[key] = value


def get_state(key: str, default=None):
    """Safely get session state value"""
    return st.session_state.get(key, default)


def set_state(key: str, value):
    """Set session state value"""
    st.session_state[key] = value