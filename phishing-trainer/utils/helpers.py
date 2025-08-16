import re
import csv
import uuid
import io
from typing import List, Dict, Any, Optional
from datetime import datetime

def parse_target_list(target_text: str) -> List[Dict[str, Any]]:
    """Parse a list of target email addresses from text input.
    
    Args:
        target_text: Text containing one email per line or CSV data
        
    Returns:
        A list of target dictionaries with email and optional name
    """
    targets = []
    
    # Check if input might be CSV
    if ',' in target_text:
        try:
            # Try to parse as CSV
            csv_reader = csv.reader(io.StringIO(target_text))
            for row in csv_reader:
                if len(row) >= 1 and row[0].strip():
                    email = row[0].strip()
                    name = row[1].strip() if len(row) >= 2 and row[1].strip() else None
                    
                    if is_valid_email(email):
                        targets.append({
                            "id": str(uuid.uuid4()),
                            "email": email,
                            "name": name,
                            "status": "queued",
                            "created_at": datetime.now().isoformat()
                        })
        except Exception:
            # If CSV parsing fails, fall back to line-by-line
            pass
    
    # If no targets were found or CSV parsing failed, try line-by-line
    if not targets:
        lines = target_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains both name and email
            match = re.match(r'([^<]+)<([^>]+)>', line)
            if match:
                name = match.group(1).strip()
                email = match.group(2).strip()
            else:
                # Assume the line is just an email
                email = line
                name = None
            
            if is_valid_email(email):
                targets.append({
                    "id": str(uuid.uuid4()),
                    "email": email,
                    "name": name,
                    "status": "queued",
                    "created_at": datetime.now().isoformat()
                })
    
    return targets

def is_valid_email(email: str) -> bool:
    """Check if a string is a valid email address.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if the email is valid, False otherwise
    """
    # Basic email validation regex
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

def format_email_template(template: str, replacements: Dict[str, str]) -> str:
    """Format an email template by replacing placeholders.
    
    Args:
        template: The email template with placeholders
        replacements: Dictionary of placeholder keys and replacement values
        
    Returns:
        The formatted template with replacements
    """
    formatted = template
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"
        formatted = formatted.replace(placeholder, value)
    return formatted

def generate_campaign_name() -> str:
    """Generate a default campaign name based on date and time.
    
    Returns:
        A campaign name string
    """
    now = datetime.now()
    return f"Campaign-{now.strftime('%Y%m%d-%H%M')}"

def format_timestamp(timestamp_str: Optional[str], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format an ISO timestamp string to a human-readable format.
    
    Args:
        timestamp_str: ISO format timestamp string
        format_str: The desired output format
        
    Returns:
        Formatted timestamp string
    """
    if not timestamp_str:
        return ""
        
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime(format_str)
    except (ValueError, TypeError):
        return timestamp_str

def calculate_click_rate(sent: int, clicked: int) -> float:
    """Calculate the click-through rate.
    
    Args:
        sent: Number of emails sent
        clicked: Number of links clicked
        
    Returns:
        Click-through rate as a percentage
    """
    if sent == 0:
        return 0.0
    return (clicked / sent) * 100

def anonymize_email(email: str, level: str = "partial") -> str:
    """Anonymize an email address for privacy.
    
    Args:
        email: The email address to anonymize
        level: The anonymization level ("none", "partial", "full")
        
    Returns:
        Anonymized email string
    """
    if level == "none":
        return email
    
    if level == "full":
        # Replace with hash
        import hashlib
        return hashlib.md5(email.encode()).hexdigest()[:8] + "@redacted"
    
    # Partial anonymization (default)
    parts = email.split('@')
    if len(parts) != 2:
        return email
    
    username, domain = parts
    if len(username) <= 2:
        masked_username = username[0] + '*' * (len(username) - 1)
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        tld = domain_parts[-1]
        domain_name = '.'.join(domain_parts[:-1])
        if len(domain_name) <= 2:
            masked_domain = domain_name[0] + '*' * (len(domain_name) - 1)
        else:
            masked_domain = domain_name[0] + '*' * (len(domain_name) - 2) + domain_name[-1]
        
        return f"{masked_username}@{masked_domain}.{tld}"
    
    return f"{masked_username}@{domain}"

def export_campaign_to_csv(campaign: Dict[str, Any], anonymize_level: str = "none") -> str:
    """Export campaign data to CSV format.
    
    Args:
        campaign: The campaign data dictionary
        anonymize_level: Level of email anonymization ("none", "partial", "full")
        
    Returns:
        CSV data as a string
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Recipient ID", "Email", "Name", "Status", 
        "Sent Time", "Click Time", "Quiz Completed", "Quiz Score"
    ])
    
    # Write data for each target
    for target in campaign.get("targets", []):
        email = anonymize_email(target.get("email", ""), anonymize_level)
        writer.writerow([
            target.get("id", ""),
            email,
            target.get("name", ""),
            target.get("status", "queued"),
            format_timestamp(target.get("sent_at")),
            format_timestamp(target.get("clicked_at")),
            "Yes" if target.get("quiz_completed") else "No",
            target.get("quiz_score", "")
        ])
    
    return output.getvalue()

def get_email_domain(email: str) -> Optional[str]:
    """Extract the domain from an email address.
    
    Args:
        email: The email address
        
    Returns:
        The domain part of the email, or None if invalid
    """
    parts = email.split('@')
    if len(parts) == 2:
        return parts[1]
    return None

def group_targets_by_domain(targets: List[Dict[str, Any]]) -> Dict[str, int]:
    """Group targets by email domain and count.
    
    Args:
        targets: List of target dictionaries
        
    Returns:
        Dictionary mapping domains to counts
    """
    domain_counts = {}
    for target in targets:
        email = target.get("email", "")
        domain = get_email_domain(email)
        if domain:
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    return domain_counts