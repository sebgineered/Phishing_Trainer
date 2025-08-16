import os
import json
import random
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import LLM providers based on configuration
try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import anthropic
except ImportError:
    anthropic = None

class EmailGenerator:
    """Service for generating phishing email content using AI."""
    
    def __init__(self):
        """Initialize the email generator with available LLM providers."""
        self.llm_provider = os.environ.get("LLM_PROVIDER", "OpenAI").lower()
        
        # Load fallback templates
        self.templates_path = Path("templates/phishing_templates.json")
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load fallback phishing templates from JSON file."""
        if not self.templates_path.exists():
            # Create templates directory if it doesn't exist
            self.templates_path.parent.mkdir(exist_ok=True)
            
            # Create default templates file with basic examples
            default_templates = {
                "credential-theft": [
                    {
                        "subject": "Urgent: Your {{company}} account needs verification",
                        "body_html": "<p>Dear User,</p><p>We have detected unusual activity on your {{company}} account. Please verify your account immediately by clicking <a href='{{tracking_url}}'>here</a>.</p><p>Regards,<br>{{company}} Security Team</p>"
                    },
                    {
                        "subject": "Security Alert: Sign-in attempt from new device",
                        "body_html": "<p>Hello,</p><p>We detected a sign-in attempt from a new device. If this was you, please confirm by clicking <a href='{{tracking_url}}'>here</a>.</p><p>If this wasn't you, your account may be at risk.</p><p>Thanks,<br>{{company}} Account Security</p>"
                    }
                ],
                "invoice": [
                    {
                        "subject": "Your {{company}} invoice #INV-29581",
                        "body_html": "<p>Hello,</p><p>Your invoice #INV-29581 from {{company}} is ready to view. Please <a href='{{tracking_url}}'>click here</a> to view and pay your invoice.</p><p>Thank you for your business.</p><p>{{company}} Billing Team</p>"
                    }
                ],
                "oauth-consent": [
                    {
                        "subject": "App permissions required for {{company}} services",
                        "body_html": "<p>Hello,</p><p>An application is requesting permission to access your {{company}} account data. Please <a href='{{tracking_url}}'>review and approve</a> these permissions to continue using our services.</p><p>{{company}} Integration Team</p>"
                    }
                ],
                "shipping": [
                    {
                        "subject": "Your {{company}} order has shipped",
                        "body_html": "<p>Hello,</p><p>Your recent order from {{company}} has shipped! <a href='{{tracking_url}}'>Click here</a> to track your package.</p><p>Thank you for shopping with us.</p><p>{{company}} Shipping Team</p>"
                    }
                ],
                "account-verification": [
                    {
                        "subject": "Verify your {{company}} account",
                        "body_html": "<p>Dear Customer,</p><p>Please verify your {{company}} account to ensure continued access to our services. <a href='{{tracking_url}}'>Click here</a> to complete verification.</p><p>{{company}} Account Team</p>"
                    }
                ],
                "password-reset": [
                    {
                        "subject": "{{company}} password reset request",
                        "body_html": "<p>Hello,</p><p>We received a request to reset your {{company}} account password. <a href='{{tracking_url}}'>Click here</a> to set a new password.</p><p>If you didn't request this, please ignore this email.</p><p>{{company}} Support Team</p>"
                    }
                ],
                "document-share": [
                    {
                        "subject": "Important document shared with you",
                        "body_html": "<p>Hello,</p><p>An important document from {{company}} has been shared with you. <a href='{{tracking_url}}'>Click here</a> to view and download.</p><p>{{company}} Document Team</p>"
                    }
                ]
            }
            
            # Save default templates
            with open(self.templates_path, 'w') as f:
                json.dump(default_templates, f, indent=2)
            
            return default_templates
        
        try:
            with open(self.templates_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {}
    
    def generate(self, company_name: str, scenario_type: str, difficulty: int = 3, 
                company_website: Optional[str] = None, custom_instructions: Optional[str] = None) -> Dict[str, str]:
        """Generate phishing email content using AI or fallback templates.
        
        Args:
            company_name: The name of the company to impersonate
            scenario_type: The type of phishing scenario (credential-theft, invoice, etc.)
            difficulty: The difficulty level (1-5) with higher being more sophisticated
            company_website: Optional website URL to scrape for company tone/style
            custom_instructions: Optional custom instructions for the AI
            
        Returns:
            Dictionary containing subject and body_html for the phishing email
        """
        # Try to generate with AI first
        try:
            if self.llm_provider == "openai" and openai and os.environ.get("OPENAI_API_KEY"):
                return self._generate_with_openai(company_name, scenario_type, difficulty, company_website, custom_instructions)
            elif self.llm_provider == "gemini" and genai and os.environ.get("GEMINI_API_KEY"):
                return self._generate_with_gemini(company_name, scenario_type, difficulty, company_website, custom_instructions)
            elif self.llm_provider == "anthropic" and anthropic and os.environ.get("ANTHROPIC_API_KEY"):
                return self._generate_with_anthropic(company_name, scenario_type, difficulty, company_website, custom_instructions)
        except Exception as e:
            print(f"Error generating with AI: {e}")
            # Fall back to templates
            pass
        
        # Fallback to templates if AI generation fails or is not configured
        return self._generate_from_template(company_name, scenario_type, difficulty)
    
    def _generate_with_openai(self, company_name: str, scenario_type: str, difficulty: int,
                             company_website: Optional[str], custom_instructions: Optional[str]) -> Dict[str, str]:
        """Generate phishing email content using OpenAI."""
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Construct the prompt
        prompt = self._construct_prompt(company_name, scenario_type, difficulty, company_website, custom_instructions)
        
        # Call the OpenAI API
        response = openai.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4"),
            messages=[
                {"role": "system", "content": "You are a security professional creating a phishing simulation for educational purposes. The email will be clearly marked as a simulation and will only use tracking links provided by the user's system. No real credentials will be collected."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Extract subject and body
        try:
            # Try to parse as JSON
            result = json.loads(content)
            return {
                "subject": result.get("subject", ""),
                "body_html": result.get("body_html", "")
            }
        except json.JSONDecodeError:
            # If not JSON, try to parse manually
            lines = content.split("\n")
            subject = ""
            body_html = ""
            
            for i, line in enumerate(lines):
                if line.startswith("Subject:") or line.startswith("SUBJECT:"):
                    subject = line.split(":", 1)[1].strip()
                elif line.startswith("<html") or line.startswith("<!DOCTYPE") or line.startswith("<body"):
                    body_html = "\n".join(lines[i:])
                    break
            
            if not body_html and "<p>" in content:
                # If we couldn't find HTML tags but there are paragraph tags, wrap in basic HTML
                body_html = f"<html><body>{content}</body></html>"
            
            return {
                "subject": subject,
                "body_html": body_html or content
            }
    
    def _generate_with_gemini(self, company_name: str, scenario_type: str, difficulty: int,
                             company_website: Optional[str], custom_instructions: Optional[str]) -> Dict[str, str]:
        """Generate phishing email content using Google Gemini."""
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        
        # Construct the prompt
        prompt = self._construct_prompt(company_name, scenario_type, difficulty, company_website, custom_instructions)
        
        # Call the Gemini API
        model = genai.GenerativeModel(os.environ.get("GEMINI_MODEL", "gemini-pro"))
        response = model.generate_content(
            [
                "You are a security professional creating a phishing simulation for educational purposes. "
                "The email will be clearly marked as a simulation and will only use tracking links provided by the user's system. "
                "No real credentials will be collected.",
                prompt
            ]
        )
        
        # Parse the response
        content = response.text
        
        # Extract subject and body (similar to OpenAI parsing)
        try:
            # Try to parse as JSON
            result = json.loads(content)
            return {
                "subject": result.get("subject", ""),
                "body_html": result.get("body_html", "")
            }
        except json.JSONDecodeError:
            # If not JSON, try to parse manually
            lines = content.split("\n")
            subject = ""
            body_html = ""
            
            for i, line in enumerate(lines):
                if line.startswith("Subject:") or line.startswith("SUBJECT:"):
                    subject = line.split(":", 1)[1].strip()
                elif line.startswith("<html") or line.startswith("<!DOCTYPE") or line.startswith("<body"):
                    body_html = "\n".join(lines[i:])
                    break
            
            if not body_html and "<p>" in content:
                # If we couldn't find HTML tags but there are paragraph tags, wrap in basic HTML
                body_html = f"<html><body>{content}</body></html>"
            
            return {
                "subject": subject,
                "body_html": body_html or content
            }
    
    def _generate_with_anthropic(self, company_name: str, scenario_type: str, difficulty: int,
                               company_website: Optional[str], custom_instructions: Optional[str]) -> Dict[str, str]:
        """Generate phishing email content using Anthropic Claude."""
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        
        # Construct the prompt
        prompt = self._construct_prompt(company_name, scenario_type, difficulty, company_website, custom_instructions)
        
        # Call the Anthropic API
        response = client.messages.create(
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            max_tokens=2000,
            system="You are a security professional creating a phishing simulation for educational purposes. The email will be clearly marked as a simulation and will only use tracking links provided by the user's system. No real credentials will be collected.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the response
        content = response.content[0].text
        
        # Extract subject and body (similar to OpenAI parsing)
        try:
            # Try to parse as JSON
            result = json.loads(content)
            return {
                "subject": result.get("subject", ""),
                "body_html": result.get("body_html", "")
            }
        except json.JSONDecodeError:
            # If not JSON, try to parse manually
            lines = content.split("\n")
            subject = ""
            body_html = ""
            
            for i, line in enumerate(lines):
                if line.startswith("Subject:") or line.startswith("SUBJECT:"):
                    subject = line.split(":", 1)[1].strip()
                elif line.startswith("<html") or line.startswith("<!DOCTYPE") or line.startswith("<body"):
                    body_html = "\n".join(lines[i:])
                    break
            
            if not body_html and "<p>" in content:
                # If we couldn't find HTML tags but there are paragraph tags, wrap in basic HTML
                body_html = f"<html><body>{content}</body></html>"
            
            return {
                "subject": subject,
                "body_html": body_html or content
            }
    
    def _construct_prompt(self, company_name: str, scenario_type: str, difficulty: int,
                         company_website: Optional[str], custom_instructions: Optional[str]) -> str:
        """Construct a prompt for the AI model."""
        difficulty_descriptions = {
            1: "very obvious phishing with multiple red flags (misspellings, urgent language, generic greeting)",
            2: "somewhat obvious with a few clear indicators",
            3: "moderately convincing but with subtle clues",
            4: "highly convincing with minimal indicators",
            5: "extremely sophisticated and difficult to detect"
        }
        
        scenario_descriptions = {
            "Credential Theft": "request for login credentials due to account issues",
            "Invoice/Payment": "notification about an invoice or payment",
            "OAuth Consent": "request to authorize an application",
            "Shipping Notification": "update about a package or shipment",
            "Account Verification": "request to verify account information",
            "Password Reset": "notification about password reset",
            "Document Share": "shared document requiring review"
        }
        
        # Normalize scenario type
        normalized_scenario = scenario_type.lower().replace("/", "-").replace(" ", "-")
        scenario_desc = scenario_descriptions.get(scenario_type, f"a {scenario_type} notification")
        
        prompt = f"""
        Create a phishing email template for a simulated security awareness training campaign with the following parameters:
        
        - Company to impersonate: {company_name}
        - Scenario type: {scenario_desc}
        - Difficulty level: {difficulty} - {difficulty_descriptions.get(difficulty, "moderate difficulty")}
        
        Requirements:
        1. The email should look realistic but include subtle indicators of phishing based on the difficulty level.
        2. Include a tracking link placeholder {{tracking_url}} that will be replaced with an actual tracking URL.
        3. Do not include any actual malicious content or real credential collection.
        4. The email is for educational purposes only.
        5. Return your response in the following format:
           - Subject line
           - HTML body with the tracking link
        
        Format your response as a JSON object with 'subject' and 'body_html' fields.
        """
        
        if company_website:
            prompt += f"\n\nCompany website for reference: {company_website}"
        
        if custom_instructions:
            prompt += f"\n\nAdditional instructions: {custom_instructions}"
        
        return prompt
    
    def _generate_from_template(self, company_name: str, scenario_type: str, difficulty: int) -> Dict[str, str]:
        """Generate phishing email content from templates."""
        # Normalize scenario type to match template keys
        normalized_scenario = scenario_type.lower().replace("/", "-").replace(" ", "-")
        
        # Get templates for this scenario type, or use a default if not found
        scenario_templates = self.templates.get(normalized_scenario, [])
        if not scenario_templates:
            # Try to find a similar scenario type
            for key in self.templates.keys():
                if normalized_scenario in key or key in normalized_scenario:
                    scenario_templates = self.templates[key]
                    break
        
        # If still no templates, use a random category
        if not scenario_templates and self.templates:
            scenario_templates = random.choice(list(self.templates.values()))
        
        # If we have templates, choose one and customize it
        if scenario_templates:
            template = random.choice(scenario_templates)
            
            # Replace placeholders
            subject = template["subject"].replace("{{company}}", company_name)
            body_html = template["body_html"].replace("{{company}}", company_name)
            
            return {
                "subject": subject,
                "body_html": body_html
            }
        
        # Fallback if no templates are available
        return {
            "subject": f"Important message from {company_name}",
            "body_html": f"<p>This is an important message from {company_name}. Please <a href='{{tracking_url}}'>click here</a> to view.</p>"
        }