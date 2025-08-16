import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, TrackingSettings, ClickTracking
from email_validator import validate_email, EmailNotValidError

from config import Config

class EmailAgent:
    """Email communication class for Jentic integration.
    
    This class handles sending emails through SendGrid, with tracking capabilities
    for phishing simulation campaigns.
    """
    
    def __init__(self):
        """Initialize the EmailAgent with API credentials."""
        self.api_key = Config.SENDGRID_API_KEY
        self.sender_email = Config.EMAIL_SENDER
        self.client = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize SendGrid client if API key is available
        if self.api_key:
            try:
                self.client = SendGridAPIClient(self.api_key)
                self.logger.info("SendGrid client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize SendGrid client: {e}")
        else:
            self.logger.warning("SendGrid API key not found. Email functionality will be limited.")
    
    def validate_email_address(self, email):
        """Validate an email address format.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def send_email(self, to_email, subject, content, is_html=True, tracking=True, campaign_id=None):
        """Send an email using SendGrid.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            content (str): Email content (HTML or plain text)
            is_html (bool): Whether content is HTML (default: True)
            tracking (bool): Enable click tracking (default: True)
            campaign_id (str, optional): Campaign ID for tracking
            
        Returns:
            dict: Response from SendGrid API
        """
        if not self.client:
            self.logger.error("SendGrid client not initialized. Cannot send email.")
            return {"success": False, "error": "SendGrid client not initialized"}
        
        # Validate email addresses
        if not self.validate_email_address(to_email):
            self.logger.error(f"Invalid recipient email address: {to_email}")
            return {"success": False, "error": f"Invalid recipient email: {to_email}"}
        
        if not self.validate_email_address(self.sender_email):
            self.logger.error(f"Invalid sender email address: {self.sender_email}")
            return {"success": False, "error": f"Invalid sender email: {self.sender_email}"}
        
        # Create message
        content_type = "text/html" if is_html else "text/plain"
        message = Mail(
            from_email=Email(self.sender_email),
            to_emails=To(to_email),
            subject=subject,
            content=Content(content_type, content)
        )
        
        # Add tracking settings if enabled
        if tracking:
            tracking_settings = TrackingSettings()
            tracking_settings.click_tracking = ClickTracking(enable=True, enable_text=True)
            message.tracking_settings = tracking_settings
        
        # Add custom campaign ID if provided
        if campaign_id:
            message.custom_args = {"campaign_id": campaign_id}
        
        # Send email
        try:
            response = self.client.send(message)
            self.logger.info(f"Email sent successfully to {to_email}. Status code: {response.status_code}")
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Email sent successfully"
            }
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}
    
    def send_phishing_email(self, to_email, subject, content, campaign_id, tracking_url=None):
        """Send a phishing simulation email with tracking.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            content (str): Email content (HTML)
            campaign_id (str): Campaign ID for tracking
            tracking_url (str, optional): Custom tracking URL
            
        Returns:
            dict: Response from SendGrid API
        """
        # If a tracking URL is provided, insert it into the content
        if tracking_url:
            # This is a simplified example - in a real implementation,
            # you would want to insert the tracking URL more intelligently
            if "<a href=\"#\"" in content:
                content = content.replace("<a href=\"#\"", f'<a href="{tracking_url}"')
        
        # Add a hidden tracking pixel if not in debug mode
        if not Config.DEBUG_MODE:
            tracking_pixel = f'<img src="https://your-tracking-server.com/pixel/{campaign_id}" style="display:none;" />'
            if "</body>" in content:
                content = content.replace("</body>", f"{tracking_pixel}</body>")
            else:
                content += tracking_pixel
        
        # Send the email with tracking enabled
        return self.send_email(
            to_email=to_email,
            subject=subject,
            content=content,
            is_html=True,
            tracking=True,
            campaign_id=campaign_id
        )
    
    def send_training_email(self, to_email, subject, content, campaign_id=None):
        """Send a training email after a phishing simulation.
        
        Args:
            to_email (str): Recipient email address
            subject (str): Email subject
            content (str): Email content (HTML)
            campaign_id (str, optional): Campaign ID for tracking
            
        Returns:
            dict: Response from SendGrid API
        """
        # Add a clear training header to the content
        training_header = (
            '<div style="background-color: #f8f9fa; padding: 10px; margin-bottom: 20px; '
            'border-left: 4px solid #28a745;">' 
            '<h3 style="color: #28a745;">Security Awareness Training</h3>' 
            '<p>This email contains important security training information.</p>' 
            '</div>'
        )
        
        if "<body>" in content:
            content = content.replace("<body>", f"<body>{training_header}")
        else:
            content = f"{training_header}{content}"
        
        # Send the email
        return self.send_email(
            to_email=to_email,
            subject=subject,
            content=content,
            is_html=True,
            tracking=True,
            campaign_id=campaign_id
        )