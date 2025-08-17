"""
Manages phishing email templates and content generation.

This module stores the available phishing scenarios and provides a function
to generate email content based on a selected scenario. New templates can be
added to the `TEMPLATES` dictionary.

Available scenarios:
- Credential Theft
- Password Reset
- Document Share
"""

from typing import Dict


TEMPLATES = {
    "Credential Theft": {
        "subject": "Action Required: Verify Your {company_name} Account",
        "body": """
        <p>Dear User,</p>
        <p>We have detected unusual activity on your {company_name} account. To ensure your account security, please verify your credentials by clicking the link below:</p>
        <p><a href=\"{{tracking_url}}\">Verify Account Now</a></p>
        <p>If you did not request this verification, please ignore this email.</p>
        <p>Thank you,<br>{company_name} Security Team</p>
        """
    },
    "Password Reset": {
        "subject": "Password Reset Request for {company_name}",
        "body": """
        <p>Dear User,</p>
        <p>We received a request to reset your password for your {company_name} account. Click the link below to set a new password:</p>
        <p><a href=\"{{tracking_url}}\">Reset Password</a></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>Regards,<br>{company_name} Support</p>
        """
    },
    "Document Share": {
        "subject": "Important Document Shared With You",
        "body": """
        <p>Hello,</p>
        <p>An important document has been shared with you from {company_name}. Please review it as soon as possible by clicking the link below:</p>
        <p><a href=\"{{tracking_url}}\">View Document</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>Best regards,<br>{company_name} Team</p>
        """
    }
}


def generate_email_template(company_name: str, scenario: str) -> Dict[str, str]:
    """
    Generates a phishing email subject and body from a template.

    Args:
        company_name: The name of the company to use in the email.
        scenario: The name of the phishing scenario to use.

    Returns:
        A dictionary containing the email subject and HTML body.
    """
    template = TEMPLATES.get(scenario, TEMPLATES["Credential Theft"])
    
    # The placeholders in the template are for jinja2-like templating, 
    # but the original code used .format(). 
    # The user's description for this file mentions `generate_email_template` which I am implementing.
    # The original `generate_simple_email_from_template` did not do any formatting.
    # I will replicate the original behavior and not format the string here, 
    # as the tracking_url is not available yet.
    # The original code replaces {{tracking_url}} later.
    # However, the company_name can be formatted.
    
    subject = template["subject"].format(company_name=company_name)
    body = template["body"].format(company_name=company_name)

    return {
        "subject": subject,
        "body_html": body
    }
