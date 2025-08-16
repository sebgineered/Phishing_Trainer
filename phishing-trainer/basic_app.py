import streamlit as st
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import asyncio

from jentic import Jentic, ExecutionRequest
from jentic.lib.cfg import AgentConfig

# Load environment variables from .env file
load_dotenv()

# Initialize session state
def init_session_state():
    if 'campaigns' not in st.session_state:
        st.session_state.campaigns = load_campaigns()
    if 'current_campaign' not in st.session_state:
        st.session_state.current_campaign = None
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'

# Load campaigns from JSON file
def load_campaigns():
    campaigns_file = Path("data/campaigns.json")
    if not campaigns_file.exists():
        return {}
    
    try:
        with open(campaigns_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading campaigns: {e}")
        return {}

# Save campaigns to JSON file
def save_campaigns():
    campaigns_file = Path("data/campaigns.json")
    campaigns_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(campaigns_file, 'w') as f:
            json.dump(st.session_state.campaigns, f, indent=2)
    except Exception as e:
        st.error(f"Error saving campaigns: {e}")

# Navigation
def navigate_to(page):
    st.session_state.page = page

# Jentic Standard Agent client for email generation
class JenticStandardAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("JENTIC_AGENT_API_KEY")
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'RuntimeError: There is no current event loop...'
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        self.client = Jentic(AgentConfig(agent_api_key=self.api_key)) if self.api_key else None
        self.connected = self.client is not None

    async def send_phishing_email(self, company_name, scenario_type, target_email):
        """Sends a phishing email using Jentic's Standard Agent with Mailchimp integration.
        
        Args:
            company_name: The company name to use in the email
            scenario_type: The type of phishing scenario
            target_email: The target email for personalization
            
        Returns:
            bool: True if the email was sent successfully, False otherwise
        """
        if not self.connected:
            st.error("Jentic client not connected. Please check your API key.")
            return False
        
        try:
            # Search for the mailchimp operation
            search_result = await self.client.search("send email with mailchimp")
            
            if not search_result.operations:
                st.error("Could not find the send email operation in Jentic.")
                return False

            print("Operation Input Schema:", search_result.operations[0].model_dump_json(indent=2))

            operation_id = search_result.operations[0].id
            
            email_content = generate_simple_email_from_template(company_name, scenario_type)

            request = ExecutionRequest(
                id=operation_id, 
                inputs={
                    "subject": email_content["subject"],
                    "body": email_content["body_html"],
                    "recipients": [{"email": target_email}],
                }
            )
            
            result = await self.client.execute(request)
            
            if result.is_success:
                return True
            else:
                st.error(f"Failed to send email to {target_email} via Jentic: {result.error}")
                return False

        except Exception as e:
            print(f"An error occurred with the Jentic client: {e}")
            import traceback
            traceback.print_exc()
            st.error(f"An error occurred with the Jentic client: {e}")
            return False


# Generate a simple phishing email from template
def generate_simple_email_from_template(company_name, scenario_type):
    templates = {
        "Credential Theft": {
            "subject": f"Action Required: Verify Your {company_name} Account",
            "body": f"""
            <p>Dear User,</p>
            <p>We have detected unusual activity on your {company_name} account. To ensure your account security, please verify your credentials by clicking the link below:</p>
            <p><a href=\"{{tracking_url}}\">Verify Account Now</a></p>
            <p>If you did not request this verification, please ignore this email.</p>
            <p>Thank you,<br>{company_name} Security Team</p>
            """
        },
        "Password Reset": {
            "subject": f"Password Reset Request for {company_name}",
            "body": f"""
            <p>Dear User,</p>
            <p>We received a request to reset your password for your {company_name} account. Click the link below to set a new password:</p>
            <p><a href=\"{{tracking_url}}\">Reset Password</a></p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <p>Regards,<br>{company_name} Support</p>
            """
        },
        "Document Share": {
            "subject": f"Important Document Shared With You",
            "body": f"""
            <p>Hello,</p>
            <p>An important document has been shared with you from {company_name}. Please review it as soon as possible by clicking the link below:</p>
            <p><a href=\"{{tracking_url}}\">View Document</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>Best regards,<br>{company_name} Team</p>
            """
        }
    }
    
    # Default to Credential Theft if scenario not found
    template = templates.get(scenario_type, templates["Credential Theft"])
    
    return {
        "subject": template["subject"],
        "body_html": template["body"]
    }

# Generate a tracking URL (simplified)
def generate_tracking_url(campaign_id, recipient_id):
    base_url = "http://localhost:8501/track"
    return f"{base_url}?cid={campaign_id}&rid={recipient_id}"

# Parse target emails
def parse_targets(target_emails):
    if not target_emails:
        return []
        
    email_list = [email.strip() for email in target_emails.split('\n') if email.strip()]
    return [{'email': email, 'id': str(uuid.uuid4()), 'status': 'queued'} for email in email_list]

# Main app
def main():
    # Page config
    st.set_page_config(
        page_title="Basic Phishing Simulation",
        page_icon="🎣",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎣 Phishing Trainer")
        st.button("Dashboard", on_click=navigate_to, args=("dashboard",))
        st.button("Create Campaign", on_click=navigate_to, args=("create_campaign",))
        st.button("Reports", on_click=navigate_to, args=("reports",))
        st.button("Settings", on_click=navigate_to, args=("settings",))
        
        st.divider()
        st.info("This is a basic phishing simulation tool for educational purposes only.")
    
    # Page router
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "create_campaign":
        show_create_campaign()
    elif st.session_state.page == "email_preview":
        show_email_preview()
    elif st.session_state.page == "reports":
        show_reports()
    elif st.session_state.page == "settings":
        show_settings()

# Dashboard page
def show_dashboard():
    st.title("Dashboard")
    
    if not st.session_state.campaigns:
        st.info("No campaigns yet. Create your first campaign!")
        st.button("Create Campaign", on_click=navigate_to, args=("create_campaign",))
        return
    
    # Display campaign summary
    st.subheader("Campaign Summary")
    
    # Create metrics
    col1, col2 = st.columns(2)
    
    total_campaigns = len(st.session_state.campaigns)
    total_targets = sum(len(campaign.get('recipients', [])) for campaign in st.session_state.campaigns.values())
    
    col1.metric("Total Campaigns", total_campaigns)
    col2.metric("Total Targets", total_targets)
    
    # Recent campaigns
    st.subheader("Recent Campaigns")
    
    for campaign_id, campaign in list(st.session_state.campaigns.items())[-5:]:
        with st.expander(f"{campaign['name']} ({campaign['created_at']})"):
            st.write(f"**Status:** {campaign['status']}")
            st.write(f"**Targets:** {len(campaign['recipients'])}")
            
            col1, col2 = st.columns(2)
            col1.button(f"View Report #{campaign_id}", key=f"report_{campaign_id}", 
                      on_click=lambda cid=campaign_id: (setattr(st.session_state, 'current_campaign', cid), navigate_to("reports")))

# Create campaign page
def show_create_campaign():
    st.title("Create Phishing Campaign")
    
    with st.form("campaign_form"):
        # Basic campaign info
        st.subheader("Campaign Details")
        campaign_name = st.text_input("Campaign Name", placeholder="MS365-Verification-Aug16")
        
        # Target selection
        st.subheader("Target Selection")
        target_emails = st.text_area("Target Emails (one per line)", placeholder="user1@example.com\nuser2@example.com")
        
        # Phishing scenario
        st.subheader("Phishing Scenario")
        company_name = st.text_input("Company/Brand Name", placeholder="Microsoft")
        
        scenario_type = st.selectbox("Scenario Type", [
            "Credential Theft", 
            "Password Reset", 
            "Document Share"
        ])
        
        # Submit button
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted:
            if not campaign_name or not company_name:
                st.error("Campaign name and company name are required.")
                return
            
            # Process target emails
            targets = parse_targets(target_emails)
            
            if not targets:
                st.error("At least one target email is required.")
                return
            
            # Create campaign
            campaign_id = str(uuid.uuid4())
            campaign = {
                'id': campaign_id,
                'name': campaign_name,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'status': 'draft',
                'company': {
                    'name': company_name
                },
                'scenario': {
                    'type': scenario_type
                },
                'recipients': targets
            }
            
            # Generate email content but don't send
            email_content = generate_simple_email_from_template(company_name, scenario_type)
            campaign['email_content'] = email_content
            
            # Generate tracking URLs
            for recipient in campaign['recipients']:
                recipient['track_url'] = generate_tracking_url(campaign_id, recipient['id'])
            
            # Save campaign
            st.session_state.campaigns[campaign_id] = campaign
            save_campaigns()
            
            # Show success message and redirect
            st.success(f"Campaign '{campaign_name}' created successfully!")
            st.session_state.current_campaign = campaign_id
            st.session_state.page = "email_preview"
            st.rerun()

# Email preview page
def show_email_preview():
    st.title("Email Preview")
    
    if not st.session_state.current_campaign or st.session_state.current_campaign not in st.session_state.campaigns:
        st.error("No campaign selected.")
        st.button("Back to Dashboard", on_click=navigate_to, args=("dashboard",))
        return
    
    campaign = st.session_state.campaigns[st.session_state.current_campaign]
    
    st.subheader(f"Campaign: {campaign['name']}")
    
    # Display email content
    st.write("**Subject:**", campaign['email_content']['subject'])
    
    # Email body preview
    st.write("**Email Body:**")
    st.code(campaign['email_content']['body_html'], language="html")
    
    # Allow editing
    with st.expander("Edit Email Content"):
        new_subject = st.text_input("Subject", value=campaign['email_content']['subject'])
        new_body = st.text_area("Body HTML", value=campaign['email_content']['body_html'], height=300)
        
        if st.button("Update Email Content"):
            campaign['email_content']['subject'] = new_subject
            campaign['email_content']['body_html'] = new_body
            st.session_state.campaigns[st.session_state.current_campaign] = campaign
            save_campaigns()
            st.success("Email content updated!")
    
    # Send campaign button
    if st.button("Send Campaign"):
        jentic_agent = JenticStandardAgent()
        if not jentic_agent.connected:
            st.error("Jentic client not connected. Please check your API key in Settings.")
            return

        # Send emails to all recipients
        with st.spinner("Sending emails..."):
            success_count = 0
            for recipient in campaign['recipients']:
                sent = asyncio.run(jentic_agent.send_phishing_email(
                    campaign['company']['name'],
                    campaign['scenario']['type'],
                    recipient['email']
                ))
                if sent:
                    success_count += 1
                    recipient['status'] = 'sent'
                    recipient['send_ts'] = datetime.now().timestamp()

        # Update campaign status
        campaign['status'] = 'active'
        st.session_state.campaigns[st.session_state.current_campaign] = campaign
        save_campaigns()
        
        st.success(f"Campaign sent! {success_count}/{len(campaign['recipients'])} emails sent successfully.")
        st.button("View Reports", on_click=navigate_to, args=("reports",))

# Reports page
def show_reports():
    st.title("Campaign Reports")
    
    if not st.session_state.campaigns:
        st.info("No campaigns available.")
        return
    
    # Campaign selector
    campaign_options = {cid: campaign['name'] for cid, campaign in st.session_state.campaigns.items()}
    
    if st.session_state.current_campaign and st.session_state.current_campaign in campaign_options:
        selected_campaign_id = st.session_state.current_campaign
    else:
        selected_campaign_id = list(campaign_options.keys())[0] if campaign_options else None
    
    if not selected_campaign_id:
        st.error("No campaigns available.")
        return
    
    selected_campaign = st.selectbox(
        "Select Campaign", 
        options=list(campaign_options.keys()),
        format_func=lambda x: campaign_options[x],
        index=list(campaign_options.keys()).index(selected_campaign_id)
    )
    
    campaign = st.session_state.campaigns[selected_campaign]
    
    # Campaign overview
    st.subheader("Campaign Overview")
    st.write(f"**Name:** {campaign['name']}")
    st.write(f"**Created:** {campaign['created_at']}")
    st.write(f"**Status:** {campaign['status']}")
    st.write(f"**Company:** {campaign['company']['name']}")
    st.write(f"**Scenario:** {campaign['scenario']['type']}")
    
    # Target statistics
    st.subheader("Target Statistics")
    
    total = len(campaign['recipients'])
    sent = sum(1 for r in campaign['recipients'] if r['status'] == 'sent')
    clicked = sum(1 for r in campaign['recipients'] if r.get('click_ts') is not None)
    
    click_rate = (clicked / sent * 100) if sent > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Targets", total)
    col2.metric("Emails Sent", sent)
    col3.metric("Clicked Link", f"{clicked} ({click_rate:.1f}%)")
    
    # Target details
    st.subheader("Target Details")
    
    # Create a dataframe for display
    import pandas as pd
    
    data = []
    for recipient in campaign['recipients']:
        data.append({
            "Email": recipient['email'],
            "Status": recipient['status'],
            "Sent": datetime.fromtimestamp(recipient['send_ts']).strftime("%Y-%m-%d %H:%M") if recipient.get('send_ts') else "-",
            "Clicked": datetime.fromtimestamp(recipient['click_ts']).strftime("%Y-%m-%d %H:%M") if recipient.get('click_ts') else "-"
        })
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        st.info("No target data available.")

# Tracking endpoint (simplified)
def track_click():
    # Get query parameters
    query_params = st.query_params
    campaign_id = query_params.get("cid", [""])[0]
    recipient_id = query_params.get("rid", [""])[0]
    
    if campaign_id and recipient_id:
        # Load campaigns
        campaigns = load_campaigns()
        
        # Find the campaign and recipient
        if campaign_id in campaigns:
            campaign = campaigns[campaign_id]
            for recipient in campaign['recipients']:
                if recipient['id'] == recipient_id:
                    # Record the click
                    recipient['click_ts'] = datetime.now().timestamp()
                    recipient['status'] = 'clicked'
                    
                    # Save the updated campaigns
                    with open("data/campaigns.json", 'w') as f:
                        json.dump(campaigns, f, indent=2)
                    
                    # Show awareness message
                    st.title("Phishing Awareness Training")
                    st.warning("This was a simulated phishing test.")
                    st.write("You clicked on a link in a phishing simulation email. In a real scenario, this could have led to:")
                    st.write("- Credential theft")
                    st.write("- Malware installation")
                    st.write("- Account compromise")
                    st.write("\nAlways verify the sender and be cautious of unexpected emails asking you to click links or provide information.")
                    return
    
    # If we get here, show a generic error
    st.title("Invalid Link")
    st.error("This link is invalid or has expired.")

# Settings page
def show_settings():
    st.title("Settings")
    
    # API Configuration section
    st.header("API Configuration")
    
    # Jentic API settings
    st.subheader("Jentic Integration")
    jentic_api_key = st.text_input(
        "Jentic Agent API Key", 
        value=os.getenv("JENTIC_AGENT_API_KEY", ""),
        type="password",
        help="API key for Jentic's Standard Agent integration"
    )
    
    # Email service settings
    st.subheader("Email Service")
    mailchimp_api_key = st.text_input(
        "Mailchimp API Key", 
        value=os.getenv("MAILCHIMP_API_KEY", ""),
        type="password",
        help="API key for Mailchimp email service (used by Jentic)"
    )
    
    sender_email = st.text_input(
        "Sender Email",
        value=os.getenv("EMAIL_SENDER", "phishing@example.com"),
        help="Email address used as the sender for phishing simulations"
    )
    
    # Save settings button
    if st.button("Save Settings"):
        # Save settings to .env file
        env_path = Path(".env")
        
        # Read existing .env content
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        else:
            env_lines = []
        
        # Update environment variables
        env_vars = {
            "JENTIC_AGENT_API_KEY": jentic_api_key,
            "MAILCHIMP_API_KEY": mailchimp_api_key,
            "EMAIL_SENDER": sender_email
        }
        
        # Update .env file content
        with open(env_path, 'w') as f:
            for key, value in env_vars.items():
                f.write(f'{key}="{value}"\n')
        
        # Update environment variables in current session
        for var_name, var_value in env_vars.items():
            os.environ[var_name] = var_value
        
        st.success("Settings saved successfully to .env file!")
        st.info("Note: API keys are stored in the .env file in your project directory.")

# Main entry point
if __name__ == "__main__":
    # Check if this is a tracking URL
    query_params = st.query_params
    if "cid" in query_params and "rid" in query_params:
        track_click()
    else:
        main()
