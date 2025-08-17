"""
Handles integration with external services like Jentic and Mailchimp.

This module contains the JenticStandardAgent class, which is responsible for
sending phishing emails via the Jentic platform, which in turn uses Mailchimp.
"""

import asyncio
import json
from typing import Any, Dict

import streamlit as st
from jentic import Jentic, ExecutionRequest
from jentic.lib.cfg import AgentConfig

from .config import (
    get_jentic_api_key,
    get_mailchimp_api_key,
    get_mailchimp_dc,
    get_mailchimp_api_url,
    get_mailchimp_list_id,
    get_sender_email
)
from .templates import generate_email_template


class JenticStandardAgent:
    """A client for the Jentic Standard Agent to send phishing emails."""

    def __init__(self, api_key: str = None):
        """
        Initializes the JenticStandardAgent.

        Args:
            api_key: The Jentic Agent API key. If not provided, it will be
                     retrieved from environment variables.
        """
        self.api_key = api_key or get_jentic_api_key()
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.client = Jentic(AgentConfig(agent_api_key=self.api_key)) if self.api_key else None
        self.connected = self.client is not None

    async def send_phishing_email(self, company_name: str, scenario_type: str, target_email: str) -> Any:
        """
        Sends a phishing email to a target using the Jentic platform.

        Args:
            company_name: The name of the company being impersonated.
            scenario_type: The type of phishing scenario.
            target_email: The email address of the target.

        Returns:
            The result of the Jentic execution, or False if an error occurred.
        """
        if not self.connected:
            st.error("Jentic client not connected. Please check your API key.")
            return False
        
        try:
            # Generate email content
            email_content = generate_email_template(company_name, scenario_type)
            
            # Check for required settings
            list_id = get_mailchimp_list_id()
            if not list_id:
                raise Exception("Mailchimp List ID not configured. Please check Settings.")

            # Use campaigns endpoint with correct operation ID
            operation_id = 'op_3932e8ad74c8ccf2'

            # Create execution request with proper API endpoint
            request = ExecutionRequest(
                id=operation_id,
                inputs={
                    "type": "regular",
                    "recipients": {
                        "list_id": list_id,
                        "segment_opts": {
                            "saved_segment_id": None,
                            "match": "all",
                            "conditions": [
                                {
                                    "field": "email_address",
                                    "op": "is",
                                    "value": target_email
                                }
                            ]
                        }
                    },
                    "settings": {
                        "subject_line": email_content["subject"],
                        "reply_to": get_sender_email(),
                        "from_name": f"{company_name} Security",
                        "title": f"Phishing Campaign - {company_name}",
                        "authenticate": True,
                        "auto_footer": False,
                        "inline_css": True
                    },
                    "content": {
                        "html": email_content["body_html"],
                        "plain_text": email_content["body_html"].replace("<p>", "").replace("</p>", "\n\n").replace("<br>", "\n")
                    },
                    "api_key": get_mailchimp_api_key(),
                    "dc": get_mailchimp_dc(),
                    "api_endpoint": get_mailchimp_api_url()
                }
            )
            
            result = await self.client.execute(request)
            
            if not result.success:
                raise Exception(f"Failed to send email: {result.error}")
            
            return result

        except Exception as e:
            error_msg = f"An error occurred with the Jentic client: {e}"
            st.error(error_msg)
            return False
