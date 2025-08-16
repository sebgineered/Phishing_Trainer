import logging
import openai
from typing import Dict, List, Optional

from config import Config
from models.campaign import PhishingTemplate

class PhishingGenerator:
    """Service for generating phishing email content using language models."""
    
    def __init__(self):
        """Initialize the PhishingGenerator with API credentials."""
        self.api_key = Config.OPENAI_API_KEY
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            openai.api_key = self.api_key
            self.logger.info("OpenAI client initialized successfully")
        else:
            self.logger.warning("OpenAI API key not found. Using fallback templates.")
    
    def generate_phishing_content(self, template_type: str, difficulty: int, 
                                 custom_instructions: Optional[str] = None) -> PhishingTemplate:
        """Generate phishing email content based on template type and difficulty.
        
        Args:
            template_type (str): Type of phishing template (e.g., "Password Reset")
            difficulty (int): Difficulty level from 1-5 (5 being most sophisticated)
            custom_instructions (str, optional): Custom instructions for content generation
            
        Returns:
            PhishingTemplate: Generated phishing template
        """
        # If no API key, use fallback templates
        if not self.api_key:
            return self._get_fallback_template(template_type, difficulty)
        
        # Prepare prompt based on template type and difficulty
        prompt = self._create_generation_prompt(template_type, difficulty, custom_instructions)
        
        try:
            # Call OpenAI API to generate content
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use appropriate model
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            content = response.choices[0].message.content
            parsed_content = self._parse_generated_content(content)
            
            # Create and return the template
            return PhishingTemplate(
                name=f"{template_type} (Generated)",
                subject=parsed_content.get("subject", f"Important: {template_type}"),
                content=parsed_content.get("content", ""),
                difficulty=difficulty,
                tags=[template_type.lower(), f"difficulty-{difficulty}"],
                custom=bool(custom_instructions)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate phishing content: {e}")
            # Fall back to template if generation fails
            return self._get_fallback_template(template_type, difficulty)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the language model."""
        return """
        You are a security awareness training assistant. Your task is to create realistic but safe 
        phishing email templates for educational purposes only. These templates will be used in 
        controlled phishing simulations to help organizations train their employees to recognize 
        and avoid real phishing attempts.
        
        Important guidelines:
        1. The content should be realistic enough to be educational but MUST NOT include:
           - Actual malicious code or exploits
           - Real company logos or exact brand impersonation
           - Instructions that could cause real harm if followed
        2. All generated templates must include clear indicators that a vigilant user could spot
        3. Templates should vary in sophistication based on the requested difficulty level
        4. The output should be in HTML format suitable for email delivery
        5. Include a subject line appropriate for the template type
        
        Your response should be structured as follows:
        SUBJECT: [Email subject line]
        
        CONTENT:
        [HTML content of the email]
        """
    
    def _create_generation_prompt(self, template_type: str, difficulty: int, 
                                 custom_instructions: Optional[str] = None) -> str:
        """Create a prompt for the language model based on template type and difficulty.
        
        Args:
            template_type (str): Type of phishing template
            difficulty (int): Difficulty level from 1-5
            custom_instructions (str, optional): Custom instructions
            
        Returns:
            str: Prompt for the language model
        """
        difficulty_descriptions = {
            1: "Very obvious with multiple red flags (spelling errors, generic greeting, suspicious sender)",
            2: "Somewhat obvious with a few clear indicators",
            3: "Moderately sophisticated with subtle indicators",
            4: "Sophisticated with very subtle indicators that require careful inspection",
            5: "Highly sophisticated, mimicking legitimate communications with minimal indicators"
        }
        
        template_descriptions = {
            "Password Reset": "An email claiming the user's password needs to be reset urgently",
            "Invoice Payment": "An email regarding an invoice that requires immediate payment",
            "Document Review": "An email requesting review of an important document",
            "IT Notification": "An email from IT about a system update or security issue",
            "Custom": "A custom phishing scenario"
        }
        
        base_prompt = f"""
        Please create a phishing email template with the following specifications:
        
        Template Type: {template_type}
        Description: {template_descriptions.get(template_type, 'Custom template')}
        Difficulty Level: {difficulty} - {difficulty_descriptions.get(difficulty, 'Moderate')}
        
        The email should appear to come from a generic organization and should include:
        1. A compelling subject line
        2. A sense of urgency or importance
        3. A call to action (like clicking a link or opening an attachment)
        4. HTML formatting that looks professional
        
        Remember to include subtle indicators of phishing appropriate for the difficulty level.
        """
        
        if custom_instructions:
            base_prompt += f"""
            
            Additional custom instructions:
            {custom_instructions}
            """
        
        return base_prompt
    
    def _parse_generated_content(self, content: str) -> Dict[str, str]:
        """Parse the generated content to extract subject and body.
        
        Args:
            content (str): Generated content from the language model
            
        Returns:
            Dict[str, str]: Dictionary with subject and content keys
        """
        result = {"subject": "", "content": ""}
        
        # Extract subject
        if "SUBJECT:" in content:
            parts = content.split("SUBJECT:", 1)
            subject_parts = parts[1].split("\n", 1)
            result["subject"] = subject_parts[0].strip()
            remaining = subject_parts[1] if len(subject_parts) > 1 else ""
        else:
            remaining = content
        
        # Extract content
        if "CONTENT:" in remaining:
            content_parts = remaining.split("CONTENT:", 1)
            result["content"] = content_parts[1].strip()
        else:
            # If no CONTENT marker, use everything after subject as content
            result["content"] = remaining.strip()
        
        return result
    
    def _get_fallback_template(self, template_type: str, difficulty: int) -> PhishingTemplate:
        """Get a fallback template when API generation fails.
        
        Args:
            template_type (str): Type of phishing template
            difficulty (int): Difficulty level
            
        Returns:
            PhishingTemplate: Fallback template
        """
        templates = {
            "Password Reset": {
                "subject": "Urgent: Your Password Will Expire Today",
                "content": """
                <html>
                <body>
                <p>Dear User,</p>
                <p>Our security system has detected that your password will expire in 24 hours. 
                You must reset your password immediately to avoid account lockout.</p>
                <p><a href="#">Click here to reset your password</a></p>
                <p>If you do not reset your password, your account will be locked and you will 
                need to contact IT support.</p>
                <p>Thank you,<br>IT Security Team</p>
                </body>
                </html>
                """
            },
            "Invoice Payment": {
                "subject": "Invoice #INV-2023-45678 Payment Required",
                "content": """
                <html>
                <body>
                <p>Dear Customer,</p>
                <p>This is a reminder that invoice #INV-2023-45678 for $1,249.99 is due for payment today.</p>
                <p>To avoid late fees, please process this payment immediately:</p>
                <p><a href="#">View and Pay Invoice Online</a></p>
                <p>If you have any questions, please contact our accounting department.</p>
                <p>Regards,<br>Accounts Receivable</p>
                </body>
                </html>
                """
            },
            "Document Review": {
                "subject": "Important Document Requires Your Review",
                "content": """
                <html>
                <body>
                <p>Hello,</p>
                <p>I've shared an important document that requires your immediate review and signature.</p>
                <p>The document contains confidential information regarding the upcoming project changes.</p>
                <p><a href="#">View Document</a></p>
                <p>Please review and sign by end of day.</p>
                <p>Thanks,<br>Management Team</p>
                </body>
                </html>
                """
            },
            "IT Notification": {
                "subject": "Critical Security Update Required",
                "content": """
                <html>
                <body>
                <p>Dear Employee,</p>
                <p>Our security team has detected unusual activity on your account.</p>
                <p>To secure your account, you must verify your identity and update your security settings immediately.</p>
                <p><a href="#">Verify Account & Update Security</a></p>
                <p>Failure to update your security settings may result in temporary account suspension.</p>
                <p>Regards,<br>IT Security Department</p>
                </body>
                </html>
                """
            }
        }
        
        # Default to IT Notification if template type not found
        template_data = templates.get(template_type, templates["IT Notification"])
        
        return PhishingTemplate(
            name=f"{template_type} (Fallback)",
            subject=template_data["subject"],
            content=template_data["content"],
            difficulty=difficulty,
            tags=[template_type.lower(), "fallback", f"difficulty-{difficulty}"],
            custom=False
        )