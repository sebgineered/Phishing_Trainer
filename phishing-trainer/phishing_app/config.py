"""
Handles environment variables and default settings for the phishing simulator.

This module centralizes the reading and writing of configuration parameters,
such as API keys and email settings, from a .env file. It provides
strongly typed accessor functions to retrieve these settings.
"""

import os
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_jentic_api_key() -> str:
    """Returns the Jentic Agent API key from environment variables."""
    return os.getenv("JENTIC_AGENT_API_KEY", "")


def get_mailchimp_api_key() -> str:
    """Returns the Mailchimp API key from environment variables."""
    key = os.getenv("MAILCHIMP_API_KEY", "").strip()
    if not key:
        raise ValueError("MAILCHIMP_API_KEY is required.")
    return key


def get_mailchimp_list_id() -> str:
    """Returns the Mailchimp List ID from environment variables."""
    list_id = os.getenv("MAILCHIMP_LIST_ID", "").strip()
    if not list_id:
        raise ValueError("MAILCHIMP_LIST_ID is required.")
    return list_id


def get_mailchimp_dc() -> str:
    """Returns the Mailchimp data center from environment variables."""
    return os.getenv("MAILCHIMP_DC", "us7")


def get_mailchimp_api_url() -> str:
    """Returns the Mailchimp API URL from environment variables."""
    return os.getenv("MAILCHIMP_API_URL", "https://us7.api.mailchimp.com/3.0")


def get_sender_email() -> str:
    """Returns the sender email address from environment variables."""
    return os.getenv("EMAIL_SENDER", "phishing@example.com")

def save_settings(settings: Dict[str, str]) -> None:
    """
    Saves the provided settings to the .env file and updates the environment.

    Args:
        settings: A dictionary of settings to save.
    """
    env_path = Path("../.env")
    
    # Update .env file content
    with open(env_path, 'w') as f:
        for key, value in settings.items():
            f.write(f'{key}="{value}"\n')
    
    # Update environment variables in current session
    for var_name, var_value in settings.items():
        os.environ[var_name] = var_value
