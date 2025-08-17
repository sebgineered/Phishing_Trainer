"""
Provides shared helper functions and utilities for the phishing simulator.

This module contains miscellaneous utility functions that are used across
different modules of the application, such as email validation and session
state management.
"""

import re
import streamlit as st
from .persistence import load_campaigns

def is_valid_email(email: str) -> bool:
    """
    Validates an email address using a regular expression.

    Args:
        email: The email address to validate.

    Returns:
        True if the email address is valid, False otherwise.
    """
    # A simple regex for email validation
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def init_session_state():
    """Initializes the Streamlit session state with default values."""
    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = load_campaigns()
    if 'current_campaign' not in st.session_state:
        st.session_state.current_campaign = None
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'
    if 'debug_mode' not in st.session_state:
        st.session_state.debug_mode = False

def navigate_to(page: str) -> None:
    """
    Navigates to a different page in the Streamlit application.

    Args:
        page: The name of the page to navigate to.
    """
    st.session_state.page = page
