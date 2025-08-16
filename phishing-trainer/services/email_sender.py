import os
import json
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

class EmailSender:
    """Service for sending phishing simulation emails via Mailgun."""
    
    def __init__(self):
        """Initialize the email sender service."""
        self.mailgun_api_key = os.environ.get("MAILGUN_API_KEY")
        self.mailgun_domain = os.environ.get("MAILGUN_DOMAIN")
        self.mailgun_base_url = os.environ.get(
            "MAILGUN_BASE_URL", 
            f"https://api.mailgun.net/v3/{self.mailgun_domain}"
        )
        self.from_email = os.environ.get("DEFAULT_FROM_EMAIL", f"security@{self.mailgun_domain}")
        self.from_name = os.environ.get("DEFAULT_FROM_NAME", "Security Team")
        
        # Track sent emails
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.sent_emails_file = self.data_dir / "sent_emails.json"
        self.sent_emails = self._load_sent_emails()
    
    def _load_sent_emails(self) -> List[Dict[str, Any]]:
        """Load sent emails data from file."""
        if not self.sent_emails_file.exists():
            return []
        
        try:
            with open(self.sent_emails_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sent emails data: {e}")
            return []
    
    def _save_sent_emails(self):
        """Save sent emails data to file."""
        try:
            with open(self.sent_emails_file, 'w') as f:
                json.dump(self.sent_emails, f, indent=2)
        except Exception as e:
            print(f"Error saving sent emails data: {e}")
    
    def is_configured(self) -> bool:
        """Check if the email sender is properly configured."""
        return bool(self.mailgun_api_key and self.mailgun_domain)
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                  campaign_id: str, recipient_id: str,
                  from_name: Optional[str] = None, 
                  from_email: Optional[str] = None,
                  reply_to: Optional[str] = None,
                  tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send an email via Mailgun.
        
        Args:
            to_email: The recipient's email address
            subject: The email subject
            html_content: The HTML content of the email
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            from_name: Optional sender name override
            from_email: Optional sender email override
            reply_to: Optional reply-to email address
            tags: Optional tags for the email
            
        Returns:
            A dictionary with the send result and metadata
        """
        if not self.is_configured():
            raise ValueError("Mailgun is not properly configured. Please set MAILGUN_API_KEY and MAILGUN_DOMAIN.")
        
        # Set up the sender information
        sender_name = from_name or self.from_name
        sender_email = from_email or self.from_email
        from_header = f"{sender_name} <{sender_email}>"
        
        # Prepare the email data
        data = {
            "from": from_header,
            "to": to_email,
            "subject": subject,
            "html": html_content,
            "o:tracking": "yes",
            "o:tracking-clicks": "htmlonly",
            "o:tracking-opens": "yes",
            "v:campaign_id": campaign_id,
            "v:recipient_id": recipient_id
        }
        
        # Add reply-to if provided
        if reply_to:
            data["h:Reply-To"] = reply_to
        
        # Add tags if provided
        if tags:
            for tag in tags:
                data["o:tag"] = tag
        
        # Send the email via Mailgun API
        try:
            response = requests.post(
                f"{self.mailgun_base_url}/messages",
                auth=("api", self.mailgun_api_key),
                data=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Record the sent email
            sent_email = {
                "timestamp": datetime.now().isoformat(),
                "to_email": to_email,
                "subject": subject,
                "campaign_id": campaign_id,
                "recipient_id": recipient_id,
                "mailgun_id": result.get("id"),
                "status": "sent"
            }
            
            self.sent_emails.append(sent_email)
            self._save_sent_emails()
            
            return {
                "success": True,
                "message_id": result.get("id"),
                "sent_email": sent_email
            }
            
        except requests.exceptions.RequestException as e:
            error_message = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', str(e))
                except ValueError:
                    error_message = e.response.text or str(e)
            
            # Record the failed email
            failed_email = {
                "timestamp": datetime.now().isoformat(),
                "to_email": to_email,
                "subject": subject,
                "campaign_id": campaign_id,
                "recipient_id": recipient_id,
                "status": "failed",
                "error": error_message
            }
            
            self.sent_emails.append(failed_email)
            self._save_sent_emails()
            
            return {
                "success": False,
                "error": error_message,
                "sent_email": failed_email
            }
    
    def send_batch(self, campaign_id: str, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send a batch of emails for a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            emails: A list of email dictionaries, each containing:
                    - to_email: The recipient's email address
                    - recipient_id: The ID of the recipient
                    - subject: The email subject
                    - html_content: The HTML content of the email
                    - from_name: (Optional) sender name override
                    - from_email: (Optional) sender email override
                    - reply_to: (Optional) reply-to email address
                    - tags: (Optional) tags for the email
            
        Returns:
            A dictionary with the batch send results
        """
        results = {
            "total": len(emails),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for email in emails:
            result = self.send_email(
                to_email=email["to_email"],
                subject=email["subject"],
                html_content=email["html_content"],
                campaign_id=campaign_id,
                recipient_id=email["recipient_id"],
                from_name=email.get("from_name"),
                from_email=email.get("from_email"),
                reply_to=email.get("reply_to"),
                tags=email.get("tags")
            )
            
            if result["success"]:
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(result)
        
        return results
    
    def get_sent_emails_for_campaign(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get all sent emails for a specific campaign.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            A list of sent email records for the campaign
        """
        return [email for email in self.sent_emails if email["campaign_id"] == campaign_id]
    
    def get_sent_email_for_recipient(self, campaign_id: str, recipient_id: str) -> Optional[Dict[str, Any]]:
        """Get the sent email record for a specific recipient in a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            recipient_id: The ID of the recipient
            
        Returns:
            The sent email record, or None if not found
        """
        emails = [email for email in self.sent_emails 
                 if email["campaign_id"] == campaign_id and email["recipient_id"] == recipient_id]
        
        if not emails:
            return None
        
        # Return the most recent email sent to this recipient in this campaign
        return max(emails, key=lambda email: email["timestamp"])