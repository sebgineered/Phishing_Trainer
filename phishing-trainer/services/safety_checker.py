import os
import re
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse

class SafetyChecker:
    """Service for checking the safety of phishing simulation emails."""
    
    def __init__(self):
        """Initialize the safety checker service."""
        self.virustotal_api_key = os.environ.get("VIRUSTOTAL_API_KEY")
        self.lakera_api_key = os.environ.get("LAKERA_API_KEY")
        self.allowed_domains = self._load_allowed_domains()
    
    def _load_allowed_domains(self) -> List[str]:
        """Load the list of allowed domains for links in emails."""
        # Default allowed domains (your app domain)
        default_domains = [
            urlparse(os.environ.get("STREAMLIT_APP_URL", "http://localhost:8501")).netloc,
            "localhost"
        ]
        
        # Add any additional allowed domains from environment
        additional_domains = os.environ.get("ALLOWED_LINK_DOMAINS", "")
        if additional_domains:
            default_domains.extend([d.strip() for d in additional_domains.split(",")])
        
        return default_domains
    
    def check_email_content(self, html_content: str, subject: str) -> Dict[str, Any]:
        """Check the safety of email content.
        
        Args:
            html_content: The HTML content of the email
            subject: The email subject
            
        Returns:
            A dictionary with safety check results
        """
        results = {
            "is_safe": True,
            "warnings": [],
            "extracted_links": [],
            "contains_script": False,
            "contains_external_resources": False,
            "contains_form": False
        }
        
        # Check for script tags
        if re.search(r'<script[^>]*>', html_content, re.IGNORECASE):
            results["is_safe"] = False
            results["warnings"].append("Email contains script tags which could execute malicious code")
            results["contains_script"] = True
        
        # Check for external resources (images, etc.)
        external_resources = re.findall(r'src=["\']([^"\']*)["\'']', html_content)
        if external_resources:
            results["contains_external_resources"] = True
            results["warnings"].append("Email contains external resources which could be used for tracking")
        
        # Check for forms
        if re.search(r'<form[^>]*>', html_content, re.IGNORECASE):
            results["is_safe"] = False
            results["warnings"].append("Email contains form elements which could collect credentials")
            results["contains_form"] = True
        
        # Extract and check links
        links = re.findall(r'href=["\']([^"\']*)["\'']', html_content)
        results["extracted_links"] = links
        
        # Check if links are to allowed domains
        unauthorized_links = []
        for link in links:
            # Skip anchor links and mailto links
            if link.startswith('#') or link.startswith('mailto:') or link.startswith('tel:'):
                continue
                
            try:
                parsed_url = urlparse(link)
                if parsed_url.netloc and parsed_url.netloc not in self.allowed_domains:
                    unauthorized_links.append(link)
            except Exception:
                unauthorized_links.append(link)
        
        if unauthorized_links:
            results["is_safe"] = False
            results["warnings"].append(f"Email contains links to unauthorized domains: {', '.join(unauthorized_links)}")
            results["unauthorized_links"] = unauthorized_links
        
        # Check for common phishing keywords in subject
        phishing_keywords = ["urgent", "alert", "verify", "suspended", "unusual activity", 
                            "security", "update required", "account access", "password reset"]
        
        found_keywords = [keyword for keyword in phishing_keywords if keyword.lower() in subject.lower()]
        if found_keywords:
            results["warnings"].append(f"Subject contains common phishing keywords: {', '.join(found_keywords)}")
        
        return results
    
    def check_url_safety(self, url: str) -> Dict[str, Any]:
        """Check the safety of a URL using VirusTotal API if available.
        
        Args:
            url: The URL to check
            
        Returns:
            A dictionary with URL safety check results
        """
        results = {
            "url": url,
            "is_checked": False,
            "is_safe": True,
            "warnings": []
        }
        
        # Check if URL is in allowed domains
        try:
            parsed_url = urlparse(url)
            if parsed_url.netloc and parsed_url.netloc not in self.allowed_domains:
                results["warnings"].append(f"URL domain {parsed_url.netloc} is not in the allowed list")
        except Exception as e:
            results["warnings"].append(f"Error parsing URL: {str(e)}")
        
        # Check with VirusTotal if API key is available
        if self.virustotal_api_key:
            try:
                headers = {
                    "x-apikey": self.virustotal_api_key
                }
                
                # Get URL ID (base64 encoded URL)
                import base64
                url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
                
                # Check if URL has been scanned before
                response = requests.get(
                    f"https://www.virustotal.com/api/v3/urls/{url_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results["is_checked"] = True
                    
                    # Get analysis stats
                    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    malicious = stats.get("malicious", 0)
                    suspicious = stats.get("suspicious", 0)
                    
                    if malicious > 0 or suspicious > 0:
                        results["is_safe"] = False
                        results["warnings"].append(f"URL flagged by {malicious} security vendors as malicious and {suspicious} as suspicious")
                    
                    results["virustotal_data"] = {
                        "malicious": malicious,
                        "suspicious": suspicious,
                        "harmless": stats.get("harmless", 0),
                        "undetected": stats.get("undetected", 0)
                    }
                
                elif response.status_code == 404:
                    # URL not analyzed yet, submit for analysis
                    response = requests.post(
                        "https://www.virustotal.com/api/v3/urls",
                        headers=headers,
                        data={"url": url}
                    )
                    
                    if response.status_code == 200:
                        results["is_checked"] = True
                        results["warnings"].append("URL submitted for analysis, check back later for results")
                    else:
                        results["warnings"].append(f"Error submitting URL for analysis: {response.status_code}")
                
                else:
                    results["warnings"].append(f"Error checking URL: {response.status_code}")
            
            except Exception as e:
                results["warnings"].append(f"Error checking URL with VirusTotal: {str(e)}")
        
        return results
    
    def check_content_with_lakera(self, content: str) -> Dict[str, Any]:
        """Check content for harmful or inappropriate content using Lakera Guard API if available.
        
        Args:
            content: The content to check
            
        Returns:
            A dictionary with content safety check results
        """
        results = {
            "is_checked": False,
            "is_safe": True,
            "warnings": []
        }
        
        if not self.lakera_api_key:
            return results
        
        try:
            headers = {
                "Authorization": f"Bearer {self.lakera_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.lakera.ai/v1/guard",
                headers=headers,
                json={
                    "input": content,
                    "tasks": ["harmfulness", "prompt-injection"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                results["is_checked"] = True
                results["lakera_data"] = data
                
                # Check for harmfulness
                if data.get("harmfulness", {}).get("flagged", False):
                    results["is_safe"] = False
                    results["warnings"].append("Content flagged as potentially harmful")
                
                # Check for prompt injection
                if data.get("prompt-injection", {}).get("flagged", False):
                    results["is_safe"] = False
                    results["warnings"].append("Content flagged for potential prompt injection")
            
            else:
                results["warnings"].append(f"Error checking content with Lakera: {response.status_code}")
        
        except Exception as e:
            results["warnings"].append(f"Error checking content with Lakera: {str(e)}")
        
        return results
    
    def sanitize_html(self, html_content: str) -> Tuple[str, List[str]]:
        """Sanitize HTML content to remove potentially harmful elements.
        
        Args:
            html_content: The HTML content to sanitize
            
        Returns:
            A tuple of (sanitized_html, list_of_changes_made)
        """
        changes = []
        
        # Remove script tags
        script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
        if re.search(script_pattern, html_content):
            html_content = re.sub(script_pattern, '', html_content)
            changes.append("Removed script tags")
        
        # Remove on* event handlers
        event_handler_pattern = re.compile(r'\s+on\w+=["\'][^"\'>]*["\'']', re.IGNORECASE)
        if re.search(event_handler_pattern, html_content):
            html_content = re.sub(event_handler_pattern, '', html_content)
            changes.append("Removed event handlers (onclick, onload, etc.)")
        
        # Remove form tags
        form_pattern = re.compile(r'<form[^>]*>.*?</form>', re.DOTALL | re.IGNORECASE)
        if re.search(form_pattern, html_content):
            html_content = re.sub(form_pattern, '', html_content)
            changes.append("Removed form elements")
        
        # Remove iframe tags
        iframe_pattern = re.compile(r'<iframe[^>]*>.*?</iframe>', re.DOTALL | re.IGNORECASE)
        if re.search(iframe_pattern, html_content):
            html_content = re.sub(iframe_pattern, '', html_content)
            changes.append("Removed iframe elements")
        
        # Replace external resource URLs with placeholders
        def replace_external_src(match):
            src = match.group(1)
            parsed = urlparse(src)
            if parsed.netloc and parsed.netloc not in self.allowed_domains:
                changes.append(f"Blocked external resource: {src}")
                return 'src="#blocked-external-resource"'
            return match.group(0)
        
        src_pattern = re.compile(r'src=["\']([^"\']*)["\'']', re.IGNORECASE)
        html_content = re.sub(src_pattern, replace_external_src, html_content)
        
        # Replace external links with allowed tracking links or placeholders
        def replace_external_href(match):
            href = match.group(1)
            # Skip anchor links, mailto, and tel links
            if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:'):
                return match.group(0)
                
            parsed = urlparse(href)
            if parsed.netloc and parsed.netloc not in self.allowed_domains:
                changes.append(f"Replaced external link: {href}")
                return 'href="#blocked-external-link"'
            return match.group(0)
        
        href_pattern = re.compile(r'href=["\']([^"\']*)["\'']', re.IGNORECASE)
        html_content = re.sub(href_pattern, replace_external_href, html_content)
        
        return html_content, changes