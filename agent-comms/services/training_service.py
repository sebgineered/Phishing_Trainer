import logging
from typing import Dict, List, Optional

from config import Config
from models.campaign import TrainingContent
from integrations.email_agent import EmailAgent

class TrainingService:
    """Service for delivering security awareness training content."""
    
    def __init__(self):
        """Initialize the TrainingService."""
        self.logger = logging.getLogger(__name__)
        self.email_agent = EmailAgent()
        
    def get_training_content(self, template_type: str, difficulty: int) -> TrainingContent:
        """Get appropriate training content based on the phishing template type.
        
        Args:
            template_type (str): Type of phishing template that was used
            difficulty (int): Difficulty level from 1-5
            
        Returns:
            TrainingContent: Training content to be delivered
        """
        # In a full implementation, this could fetch from a database or API
        # For now, we'll use predefined content
        return self._get_predefined_training(template_type, difficulty)
    
    def send_training_email(self, to_email: str, training_content: TrainingContent, 
                           campaign_id: Optional[str] = None) -> Dict:
        """Send a training email to a user who interacted with a phishing simulation.
        
        Args:
            to_email (str): Recipient email address
            training_content (TrainingContent): Training content to send
            campaign_id (str, optional): Campaign ID for tracking
            
        Returns:
            dict: Response from email sending operation
        """
        self.logger.info(f"Sending training email to {to_email}")
        
        # Use the email agent to send the training content
        return self.email_agent.send_training_email(
            to_email=to_email,
            subject=training_content.subject,
            content=training_content.content,
            campaign_id=campaign_id
        )
    
    def _get_predefined_training(self, template_type: str, difficulty: int) -> TrainingContent:
        """Get predefined training content based on template type.
        
        Args:
            template_type (str): Type of phishing template
            difficulty (int): Difficulty level
            
        Returns:
            TrainingContent: Predefined training content
        """
        training_content = {
            "Password Reset": {
                "subject": "Security Training: How to Identify Password Reset Phishing Attempts",
                "content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background-color: #f8f9fa; padding: 10px; border-left: 4px solid #28a745; }
                        .section { margin: 20px 0; }
                        .tip { background-color: #e9f7ef; padding: 10px; border-radius: 5px; }
                        h2 { color: #2c3e50; }
                        ul { padding-left: 20px; }
                        .footer { margin-top: 30px; font-size: 12px; color: #7f8c8d; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Security Awareness Training: Password Reset Phishing</h2>
                        </div>
                        
                        <div class="section">
                            <p>You recently encountered a simulated phishing email about a password reset. This training will help you identify similar threats in the future.</p>
                        </div>
                        
                        <div class="section">
                            <h3>How to Identify Password Reset Phishing Emails:</h3>
                            <ul>
                                <li><strong>Check the sender's email address</strong> - Legitimate password reset emails come from official company domains</li>
                                <li><strong>Hover over links before clicking</strong> - Verify the URL leads to the official website</li>
                                <li><strong>Be wary of urgency</strong> - Phishing emails often create false urgency to prompt immediate action</li>
                                <li><strong>Look for personalization</strong> - Legitimate emails often include your name, not generic terms like "User" or "Customer"</li>
                                <li><strong>Go directly to the website</strong> - Instead of clicking links, navigate directly to the official website and reset your password there</li>
                            </ul>
                        </div>
                        
                        <div class="section tip">
                            <h3>Pro Tip:</h3>
                            <p>Most companies will never ask you to provide your current password when resetting it. If an email asks for your current password, it's almost certainly a phishing attempt.</p>
                        </div>
                        
                        <div class="section">
                            <h3>What to Do If You Suspect a Phishing Email:</h3>
                            <ol>
                                <li>Don't click any links or download attachments</li>
                                <li>Report the email to your IT security team</li>
                                <li>Delete the email from your inbox</li>
                            </ol>
                        </div>
                        
                        <div class="footer">
                            <p>This training is part of your organization's security awareness program. For more information, contact your IT department.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            },
            "Invoice Payment": {
                "subject": "Security Training: Recognizing Fraudulent Invoice Emails",
                "content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background-color: #f8f9fa; padding: 10px; border-left: 4px solid #28a745; }
                        .section { margin: 20px 0; }
                        .tip { background-color: #e9f7ef; padding: 10px; border-radius: 5px; }
                        h2 { color: #2c3e50; }
                        ul { padding-left: 20px; }
                        .footer { margin-top: 30px; font-size: 12px; color: #7f8c8d; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Security Awareness Training: Invoice Fraud</h2>
                        </div>
                        
                        <div class="section">
                            <p>You recently encountered a simulated phishing email about an invoice payment. This training will help you identify similar financial fraud attempts in the future.</p>
                        </div>
                        
                        <div class="section">
                            <h3>How to Identify Fraudulent Invoice Emails:</h3>
                            <ul>
                                <li><strong>Verify the sender</strong> - Check that the email comes from a legitimate vendor email address</li>
                                <li><strong>Confirm invoice details</strong> - Verify invoice numbers, amounts, and services against your records</li>
                                <li><strong>Be suspicious of changed payment details</strong> - Always verify any changes to payment methods or account details by phone</li>
                                <li><strong>Check for pressure tactics</strong> - Fraudulent invoices often create urgency with threats of late fees or service disruption</li>
                                <li><strong>Examine the payment page</strong> - Ensure any payment page is secure (https://) and on the legitimate vendor website</li>
                            </ul>
                        </div>
                        
                        <div class="section tip">
                            <h3>Pro Tip:</h3>
                            <p>Always follow your organization's invoice verification process. For unexpected or high-value invoices, use established contact methods to verify with the vendor before processing payment.</p>
                        </div>
                        
                        <div class="section">
                            <h3>Red Flags in Invoice Emails:</h3>
                            <ul>
                                <li>Generic greetings instead of your name or company name</li>
                                <li>Grammatical errors or unusual language</li>
                                <li>Slight variations in company names, logos, or email domains</li>
                                <li>Requests for payment to new or different accounts</li>
                                <li>Unusual payment methods (gift cards, wire transfers to unfamiliar accounts)</li>
                            </ul>
                        </div>
                        
                        <div class="footer">
                            <p>This training is part of your organization's security awareness program. For more information, contact your IT department.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            },
            "Document Review": {
                "subject": "Security Training: Safely Handling Document Sharing Requests",
                "content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background-color: #f8f9fa; padding: 10px; border-left: 4px solid #28a745; }
                        .section { margin: 20px 0; }
                        .tip { background-color: #e9f7ef; padding: 10px; border-radius: 5px; }
                        h2 { color: #2c3e50; }
                        ul { padding-left: 20px; }
                        .footer { margin-top: 30px; font-size: 12px; color: #7f8c8d; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Security Awareness Training: Document Sharing Safety</h2>
                        </div>
                        
                        <div class="section">
                            <p>You recently encountered a simulated phishing email requesting document review. This training will help you safely handle document sharing requests in the future.</p>
                        </div>
                        
                        <div class="section">
                            <h3>How to Safely Handle Document Sharing Requests:</h3>
                            <ul>
                                <li><strong>Verify the sender</strong> - Confirm the email is from someone you know or expect to receive documents from</li>
                                <li><strong>Check for context</strong> - Legitimate document requests usually reference specific projects or conversations</li>
                                <li><strong>Be wary of unexpected attachments</strong> - Even from known senders, unexpected attachments may indicate a compromised account</li>
                                <li><strong>Examine document sharing links</strong> - Hover over links to verify they lead to legitimate services (Google Drive, OneDrive, Dropbox, etc.)</li>
                                <li><strong>Be suspicious of password-protected archives</strong> - Malware is often hidden in password-protected ZIP files</li>
                            </ul>
                        </div>
                        
                        <div class="section tip">
                            <h3>Pro Tip:</h3>
                            <p>When in doubt about a document sharing request, contact the sender through a different channel (phone call, messaging app) to verify they sent the document.</p>
                        </div>
                        
                        <div class="section">
                            <h3>Safe Document Handling Practices:</h3>
                            <ol>
                                <li>Use your organization's approved document sharing platforms</li>
                                <li>Enable multi-factor authentication on document sharing accounts</li>
                                <li>Keep your document viewing software updated</li>
                                <li>Scan downloaded files with antivirus software before opening</li>
                                <li>Be cautious of documents that request to "Enable Macros" or "Enable Content"</li>
                            </ol>
                        </div>
                        
                        <div class="footer">
                            <p>This training is part of your organization's security awareness program. For more information, contact your IT department.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            },
            "IT Notification": {
                "subject": "Security Training: Verifying IT Security Notifications",
                "content": """
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background-color: #f8f9fa; padding: 10px; border-left: 4px solid #28a745; }
                        .section { margin: 20px 0; }
                        .tip { background-color: #e9f7ef; padding: 10px; border-radius: 5px; }
                        h2 { color: #2c3e50; }
                        ul { padding-left: 20px; }
                        .footer { margin-top: 30px; font-size: 12px; color: #7f8c8d; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Security Awareness Training: IT Notification Safety</h2>
                        </div>
                        
                        <div class="section">
                            <p>You recently encountered a simulated phishing email disguised as an IT security notification. This training will help you verify legitimate IT communications in the future.</p>
                        </div>
                        
                        <div class="section">
                            <h3>How to Verify IT Security Notifications:</h3>
                            <ul>
                                <li><strong>Check official communication channels</strong> - Most IT departments announce major updates through official channels (intranet, company-wide emails)</li>
                                <li><strong>Verify the sender's email domain</strong> - Ensure it matches your company's official domain</li>
                                <li><strong>Be wary of urgent security threats</strong> - While some threats are urgent, extreme urgency is often a manipulation tactic</li>
                                <li><strong>Check for proper branding and formatting</strong> - Official IT communications typically follow company branding guidelines</li>
                                <li><strong>Navigate directly to IT portals</strong> - Instead of clicking email links, access your IT security portal directly</li>
                            </ul>
                        </div>
                        
                        <div class="section tip">
                            <h3>Pro Tip:</h3>
                            <p>Your IT department will never ask for your password via email. If you receive an email requesting your password or other credentials, it's a phishing attempt.</p>
                        </div>
                        
                        <div class="section">
                            <h3>Common IT Notification Phishing Tactics:</h3>
                            <ul>
                                <li>Claiming your account has been compromised</li>
                                <li>Alerting you to suspicious login attempts</li>
                                <li>Requiring immediate password changes via provided links</li>
                                <li>Threatening account suspension or loss of access</li>
                                <li>Requesting verification of account details</li>
                            </ul>
                        </div>
                        
                        <div class="footer">
                            <p>This training is part of your organization's security awareness program. For more information, contact your IT department.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        }
        
        # Default to IT Notification if template type not found
        content = training_content.get(template_type, training_content["IT Notification"])
        
        return TrainingContent(
            name=f"{template_type} Security Training",
            subject=content["subject"],
            content=content["content"],
            difficulty=difficulty,
            tags=[template_type.lower(), "security-training", f"difficulty-{difficulty}"]
        )