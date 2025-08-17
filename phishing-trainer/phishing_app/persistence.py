"""
Handles loading and saving of campaign data and tracking information.

This module is responsible for all data persistence operations, including
reading and writing campaign data from/to a JSON file. It can be extended
in the future to use a database instead of a file-based storage.
"""
import json
import logging
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def load_campaigns() -> Dict[str, Any]:
    """
    Loads campaign data from the campaigns.json file.

    Returns:
        A dictionary containing the campaign data, or an empty dictionary
        if the file does not exist or an error occurs.
    """
    campaigns_file = Path("data/campaigns.json")
    if not campaigns_file.exists():
        return {}
    
    try:
        with open(campaigns_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading campaigns: {e}")
        return {}


def save_campaigns(campaigns: Dict[str, Any]) -> None:
    """
    Saves the provided campaign data to the campaigns.json file.

    Args:
        campaigns: A dictionary containing the campaign data to save.
    """
    campaigns_file = Path("data/campaigns.json")
    campaigns_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(campaigns_file, 'w') as f:
            json.dump(campaigns, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving campaigns: {e}")





def generate_tracking_url(campaign_id: str, recipient_id: str) -> str:
    """
    Generates a unique tracking URL for a recipient in a campaign.

    Args:
        campaign_id: The ID of the campaign.
        recipient_id: The ID of the recipient.

    Returns:
        A string containing the tracking URL.
    """
    base_url = "http://localhost:8501/track"
    return f"{base_url}?cid={campaign_id}&rid={recipient_id}"

def track_click_and_save(campaign_id: str, recipient_id: str) -> bool:
    """
    Records a click for a given recipient and saves the updated campaign data.

    Args:
        campaign_id: The ID of the campaign.
        recipient_id: The ID of the recipient.

    Returns:
        True if the click was recorded successfully, False otherwise.
    """
    if campaign_id and recipient_id:
        campaigns = load_campaigns()
        
        if campaign_id in campaigns:
            campaign = campaigns[campaign_id]
            for recipient in campaign['recipients']:
                if recipient['id'] == recipient_id:
                    recipient['click_ts'] = datetime.now().timestamp()
                    recipient['status'] = 'clicked'
                    save_campaigns(campaigns)
                    return True
    return False
