import os
import uuid
import json
import time
import hashlib
import hmac
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

class TrackingService:
    """Service for generating and tracking unique URLs for phishing campaigns."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the tracking service.
        
        Args:
            base_url: The base URL for the tracking links. If None, will use the
                      STREAMLIT_APP_URL environment variable or a default localhost URL.
        """
        self.base_url = base_url or os.environ.get("STREAMLIT_APP_URL", "http://localhost:8501")
        self.secret_key = os.environ.get("TRACKING_SECRET_KEY", "default-secret-key")
        
        # Ensure data directory exists
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Path to clicks data file
        self.clicks_file = self.data_dir / "clicks.json"
        
        # Load existing clicks data if available
        self.clicks_data = self._load_clicks_data()
    
    def _load_clicks_data(self) -> List[Dict[str, Any]]:
        """Load existing clicks data from file."""
        if not self.clicks_file.exists():
            return []
        
        try:
            with open(self.clicks_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading clicks data: {e}")
            return []
    
    def _save_clicks_data(self):
        """Save clicks data to file."""
        try:
            with open(self.clicks_file, 'w') as f:
                json.dump(self.clicks_data, f, indent=2)
        except Exception as e:
            print(f"Error saving clicks data: {e}")
    
    def generate_tracking_url(self, campaign_id: str, recipient_id: str, 
                             utm_params: Optional[Dict[str, str]] = None) -> str:
        """Generate a unique tracking URL for a recipient.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            utm_params: Optional UTM parameters for analytics
            
        Returns:
            A tracking URL string
        """
        # Generate signature for verification
        signature = self._generate_signature(campaign_id, recipient_id)
        
        # Build the base tracking URL
        tracking_url = f"{self.base_url}?track=1&cid={campaign_id}&rid={recipient_id}&sig={signature}"
        
        # Add UTM parameters if provided
        if utm_params:
            for key, value in utm_params.items():
                tracking_url += f"&{key}={value}"
        
        return tracking_url
    
    def _generate_signature(self, campaign_id: str, recipient_id: str) -> str:
        """Generate an HMAC signature for the tracking URL.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            
        Returns:
            An HMAC signature as a hex string
        """
        message = f"{campaign_id}|{recipient_id}".encode()
        signature = hmac.new(
            key=self.secret_key.encode(),
            msg=message,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, campaign_id: str, recipient_id: str, signature: str) -> bool:
        """Verify that a tracking URL signature is valid.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            signature: The signature to verify
            
        Returns:
            True if the signature is valid, False otherwise
        """
        expected_signature = self._generate_signature(campaign_id, recipient_id)
        return hmac.compare_digest(signature, expected_signature)
    
    def record_click(self, campaign_id: str, recipient_id: str, ip: Optional[str] = None, 
                    user_agent: Optional[str] = None, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Record a click event for a tracking URL.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            ip: Optional IP address of the clicker (will be hashed for privacy)
            user_agent: Optional user agent string
            additional_data: Optional additional data to record
            
        Returns:
            The click event data that was recorded
        """
        # Hash the IP address for privacy if provided
        hashed_ip = None
        if ip:
            hashed_ip = hashlib.sha256(ip.encode()).hexdigest()
        
        # Create the click event
        click_event = {
            "id": str(uuid.uuid4()),
            "ts": int(time.time()),
            "timestamp": datetime.now().isoformat(),
            "campaign_id": campaign_id,
            "recipient_id": recipient_id,
            "ip_hash": hashed_ip,
            "user_agent": user_agent
        }
        
        # Add any additional data
        if additional_data:
            click_event.update(additional_data)
        
        # Add to clicks data and save
        self.clicks_data.append(click_event)
        self._save_clicks_data()
        
        return click_event
    
    def get_clicks_for_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all click events for a specific campaign.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            A list of click events for the campaign
        """
        return [click for click in self.clicks_data if click["campaign_id"] == campaign_id]
    
    def get_clicks_for_recipient(self, recipient_id: str) -> List[Dict[str, Any]]:
        """Get all click events for a specific recipient.
        
        Args:
            recipient_id: The ID of the recipient
            
        Returns:
            A list of click events for the recipient
        """
        return [click for click in self.clicks_data if click["recipient_id"] == recipient_id]
    
    def get_first_click_timestamp(self, campaign_id: str, recipient_id: str) -> Optional[int]:
        """Get the timestamp of the first click for a specific recipient in a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            
        Returns:
            The timestamp of the first click, or None if no clicks
        """
        clicks = [click for click in self.clicks_data 
                 if click["campaign_id"] == campaign_id and click["recipient_id"] == recipient_id]
        
        if not clicks:
            return None
        
        # Sort by timestamp and return the earliest
        return min(click["ts"] for click in clicks)
    
    def record_quiz_completion(self, campaign_id: str, recipient_id: str, 
                              score: int, answers: Dict[str, str]) -> Dict[str, Any]:
        """Record the completion of an awareness quiz.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            score: The quiz score (e.g., number of correct answers)
            answers: Dictionary of question IDs to answer texts
            
        Returns:
            The quiz completion event data that was recorded
        """
        quiz_event = {
            "id": str(uuid.uuid4()),
            "ts": int(time.time()),
            "timestamp": datetime.now().isoformat(),
            "campaign_id": campaign_id,
            "recipient_id": recipient_id,
            "event_type": "quiz_completion",
            "quiz_score": score,
            "quiz_answers": answers
        }
        
        # Add to clicks data and save
        self.clicks_data.append(quiz_event)
        self._save_clicks_data()
        
        return quiz_event
    
    def get_quiz_completion(self, campaign_id: str, recipient_id: str) -> Optional[Dict[str, Any]]:
        """Get the quiz completion event for a specific recipient in a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            
        Returns:
            The quiz completion event, or None if not completed
        """
        quiz_events = [event for event in self.clicks_data 
                      if event.get("event_type") == "quiz_completion" 
                      and event["campaign_id"] == campaign_id 
                      and event["recipient_id"] == recipient_id]
        
        if not quiz_events:
            return None
        
        # Return the most recent quiz completion
        return max(quiz_events, key=lambda event: event["ts"])