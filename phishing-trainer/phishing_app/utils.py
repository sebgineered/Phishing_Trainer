"""
Provides shared helper functions and utilities for the phishing simulator.

This module contains miscellaneous utility functions that are used across
different modules of the application, such as email validation and session
state management.
"""

import re
import streamlit as st
from email_validator import validate_email, EmailNotValidError
from .persistence import load_campaigns

def validate_and_normalize_email(addr: str) -> str | None:
    """Return normalized email if valid, else None."""
    try:
        valid = validate_email(addr, check_deliverability=True)
        # normalized email (lowercase domain, Unicode handling)
        return valid.email
    except EmailNotValidError:
        return None

def parse_targets(target_emails: str) -> tuple[list[str], list[str]]:
    """Split comma/line-separated emails, validate, normalize, and de duplicate."""
    valid_emails = set()
    invalid_emails = set()
    for raw in re.split(r'[,]+', target_emails):
        email = validate_and_normalize_email(raw.strip())
        if email:
            valid_emails.add(email)
        else:
            invalid_emails.add(raw.strip())
    return list(valid_emails), list(invalid_emails)

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
