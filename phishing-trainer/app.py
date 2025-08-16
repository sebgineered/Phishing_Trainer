import streamlit as st
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

# Import custom modules
from models.campaign import Campaign, Target
from services.email_generator import EmailGenerator
from services.mailgun_client import MailgunClient
from utils.tracking import TrackingManager
from utils.security import SecurityChecker

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

# Main app
def main():
    # Page config
    st.set_page_config(
        page_title="Phishing Simulation & Awareness Trainer",
        page_icon="🎣",
        layout="wide",
        initial_sidebar_state="expanded"
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
        st.info("This is a phishing simulation tool for educational purposes only.")
    
    # Page router
    if st.session_state.page == "dashboard":
        show_dashboard()
    elif st.session_state.page == "create_campaign":
        show_create_campaign()
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
    col1, col2, col3, col4 = st.columns(4)
    
    total_campaigns = len(st.session_state.campaigns)
    total_targets = sum(len(campaign.get('recipients', [])) for campaign in st.session_state.campaigns.values())
    avg_click_rate = sum(campaign.get('metrics', {}).get('click_rate', 0) for campaign in st.session_state.campaigns.values()) / total_campaigns if total_campaigns > 0 else 0
    avg_quiz_score = sum(campaign.get('metrics', {}).get('avg_quiz_score', 0) for campaign in st.session_state.campaigns.values()) / total_campaigns if total_campaigns > 0 else 0
    
    col1.metric("Total Campaigns", total_campaigns)
    col2.metric("Total Targets", total_targets)
    col3.metric("Avg. Click Rate", f"{avg_click_rate:.1%}")
    col4.metric("Avg. Quiz Score", f"{avg_quiz_score:.1f}/5")
    
    # Recent campaigns
    st.subheader("Recent Campaigns")
    
    for campaign_id, campaign in list(st.session_state.campaigns.items())[-5:]:
        with st.expander(f"{campaign['name']} ({campaign['created_at']})"):
            st.write(f"**Status:** {campaign['status']}")
            st.write(f"**Targets:** {len(campaign['recipients'])}")
            st.write(f"**Click Rate:** {campaign.get('metrics', {}).get('click_rate', 0):.1%}")
            st.write(f"**Quiz Completion:** {campaign.get('metrics', {}).get('quiz_completion_rate', 0):.1%}")
            
            col1, col2 = st.columns(2)
            col1.button(f"View Report #{campaign_id}", key=f"report_{campaign_id}", 
                      on_click=lambda cid=campaign_id: (setattr(st.session_state, 'current_campaign', cid), navigate_to("reports")))
            col2.button(f"Clone #{campaign_id}", key=f"clone_{campaign_id}",
                      on_click=lambda cid=campaign_id: clone_campaign(cid))

# Create campaign page
def show_create_campaign():
    st.title("Create Phishing Campaign")
    
    with st.form("campaign_form"):
        # Basic campaign info
        st.subheader("Campaign Details")
        campaign_name = st.text_input("Campaign Name", placeholder="MS365-Verification-Aug16")
        
        # Target selection
        st.subheader("Target Selection")
        target_input_method = st.radio("Add targets by:", ["Manual Entry", "CSV Upload"])
        
        if target_input_method == "Manual Entry":
            target_emails = st.text_area("Target Emails (one per line)", placeholder="user1@example.com\nuser2@example.com")
        else:
            target_file = st.file_uploader("Upload CSV with target emails", type=["csv"])
        
        # Phishing scenario
        st.subheader("Phishing Scenario")
        company_name = st.text_input("Company/Brand Name", placeholder="Microsoft")
        company_website = st.text_input("Company Website", placeholder="https://microsoft.com")
        company_news = st.text_input("Recent News Link (optional)", placeholder="https://news.microsoft.com/recent-update")
        
        scenario_type = st.selectbox("Scenario Type", [
            "Credential Theft", 
            "Invoice/Payment", 
            "OAuth Consent", 
            "Shipping Notification",
            "Account Verification",
            "Password Reset",
            "Document Share"
        ])
        
        difficulty = st.slider("Difficulty Level", 1, 5, 3, help="Higher difficulty means more sophisticated phishing emails")
        
        # Advanced options
        with st.expander("Advanced Options"):
            display_name = st.text_input("Sender Display Name", placeholder="Microsoft Account Team")
            reply_to = st.text_input("Reply-To Email", placeholder="no-reply@microsoft-support.com")
            sending_window = st.select_slider(
                "Sending Window",
                options=["Immediate", "Business Hours", "Spread over 24h", "Spread over 48h"],
                value="Business Hours"
            )
        
        # Submit button
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted:
            if not campaign_name or not company_name:
                st.error("Campaign name and company name are required.")
                return
            
            # Process target emails
            targets = []
            if target_input_method == "Manual Entry" and target_emails:
                email_list = [email.strip() for email in target_emails.split('\n') if email.strip()]
                targets = [{'email': email, 'id': str(uuid.uuid4()), 'status': 'queued'} for email in email_list]
            elif target_input_method == "CSV Upload" and target_file is not None:
                # Process CSV file
                import pandas as pd
                df = pd.read_csv(target_file)
                if 'email' in df.columns:
                    email_list = df['email'].tolist()
                    targets = [{'email': email, 'id': str(uuid.uuid4()), 'status': 'queued'} for email in email_list]
                else:
                    st.error("CSV file must contain an 'email' column.")
                    return
            
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
                    'name': company_name,
                    'website': company_website,
                    'news': company_news
                },
                'scenario': {
                    'type': scenario_type,
                    'difficulty': difficulty
                },
                'advanced': {
                    'display_name': display_name,
                    'reply_to': reply_to,
                    'sending_window': sending_window
                },
                'recipients': targets,
                'metrics': {
                    'click_rate': 0,
                    'quiz_completion_rate': 0,
                    'avg_quiz_score': 0
                }
            }
            
            # Save campaign
            st.session_state.campaigns[campaign_id] = campaign
            save_campaigns()
            
            # Show success message and redirect
            st.success(f"Campaign '{campaign_name}' created successfully!")
            st.session_state.current_campaign = campaign_id
            st.session_state.page = "generate_email"
            st.experimental_rerun()

# Generate email page (after campaign creation)
def show_generate_email():
    st.title("Generate Phishing Email")
    
    if not st.session_state.current_campaign or st.session_state.current_campaign not in st.session_state.campaigns:
        st.error("No campaign selected.")
        st.button("Back to Dashboard", on_click=navigate_to, args=("dashboard",))
        return
    
    campaign = st.session_state.campaigns[st.session_state.current_campaign]
    
    st.subheader(f"Campaign: {campaign['name']}")
    
    # Initialize email generator
    email_generator = EmailGenerator()
    
    # Generate email content
    if st.button("Generate Email Content"):
        with st.spinner("Generating phishing email content..."):
            # Call the email generator service
            email_content = email_generator.generate(
                company_name=campaign['company']['name'],
                company_website=campaign['company']['website'],
                scenario_type=campaign['scenario']['type'],
                difficulty=campaign['scenario']['difficulty']
            )
            
            # Store the generated content in the campaign
            campaign['email_content'] = email_content
            st.session_state.campaigns[st.session_state.current_campaign] = campaign
            save_campaigns()
    
    # Display generated content if available
    if 'email_content' in campaign:
        st.subheader("Generated Email")
        
        # Subject line
        st.write("**Subject:**", campaign['email_content']['subject'])
        
        # Email body preview
        st.write("**Email Body:**")
        st.code(campaign['email_content']['body_html'][:500] + "...", language="html")
        
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
        
        # Continue to sending
        if st.button("Continue to Sending"):
            st.session_state.page = "send_campaign"
            st.experimental_rerun()

# Send campaign page
def show_send_campaign():
    st.title("Send Campaign")
    
    if not st.session_state.current_campaign or st.session_state.current_campaign not in st.session_state.campaigns:
        st.error("No campaign selected.")
        st.button("Back to Dashboard", on_click=navigate_to, args=("dashboard",))
        return
    
    campaign = st.session_state.campaigns[st.session_state.current_campaign]
    
    if 'email_content' not in campaign:
        st.error("Email content not generated yet.")
        st.button("Generate Email Content", on_click=navigate_to, args=("generate_email",))
        return
    
    st.subheader(f"Campaign: {campaign['name']}")
    
    # Campaign summary
    st.write(f"**Targets:** {len(campaign['recipients'])} recipients")
    st.write(f"**Subject:** {campaign['email_content']['subject']}")
    
    # Security check
    security_checker = SecurityChecker()
    security_issues = security_checker.check_email_content(campaign['email_content']['body_html'])
    
    if security_issues:
        st.warning("Security Check Results:")
        for issue in security_issues:
            st.write(f"- {issue}")
    else:
        st.success("Security check passed. No issues found.")
    
    # Tracking setup
    tracking_manager = TrackingManager()
    
    # Generate tracking URLs for each recipient
    if st.button("Generate Tracking URLs"):
        with st.spinner("Generating tracking URLs..."):
            for recipient in campaign['recipients']:
                recipient['track_url'] = tracking_manager.generate_tracking_url(
                    campaign_id=campaign['id'],
                    recipient_id=recipient['id']
                )
            
            st.session_state.campaigns[st.session_state.current_campaign] = campaign
            save_campaigns()
            st.success("Tracking URLs generated!")
    
    # Send emails
    if st.button("Send Campaign"):
        if not all('track_url' in recipient for recipient in campaign['recipients']):
            st.error("Please generate tracking URLs first.")
            return
        
        mailgun_client = MailgunClient()
        
        with st.spinner("Sending emails..."):
            for recipient in campaign['recipients']:
                # Personalize email for each recipient
                personalized_html = campaign['email_content']['body_html'].replace(
                    "{{tracking_url}}", recipient['track_url']
                )
                
                # Send email via Mailgun
                send_result = mailgun_client.send_email(
                    to_email=recipient['email'],
                    subject=campaign['email_content']['subject'],
                    html_content=personalized_html,
                    from_name=campaign['advanced'].get('display_name', campaign['company']['name']),
                    reply_to=campaign['advanced'].get('reply_to', '')
                )
                
                if send_result['success']:
                    recipient['status'] = 'sent'
                    recipient['send_ts'] = datetime.now().timestamp()
                    recipient['message_id'] = send_result.get('message_id', '')
                else:
                    recipient['status'] = 'failed'
                    recipient['error'] = send_result.get('error', 'Unknown error')
            
            # Update campaign status
            campaign['status'] = 'active'
            st.session_state.campaigns[st.session_state.current_campaign] = campaign
            save_campaigns()
            
            st.success("Campaign sent successfully!")
            st.button("View Reports", on_click=navigate_to, args=("reports",))

# Reports page
def show_reports():
    st.title("Campaign Reports")
    
    if not st.session_state.campaigns:
        st.info("No campaigns available.")
        return
    
    # Campaign selector
    campaign_options = {cid: campaign['name'] for cid, campaign in st.session_state.campaigns.items()}
    selected_campaign = st.selectbox(
        "Select Campaign", 
        options=list(campaign_options.keys()),
        format_func=lambda x: campaign_options[x],
        index=list(campaign_options.keys()).index(st.session_state.current_campaign) if st.session_state.current_campaign in campaign_options else 0
    )
    
    campaign = st.session_state.campaigns[selected_campaign]
    
    # Campaign overview
    st.subheader("Campaign Overview")
    col1, col2, col3 = st.columns(3)
    
    # Calculate metrics
    total_recipients = len(campaign['recipients'])
    sent_count = sum(1 for r in campaign['recipients'] if r['status'] in ['sent', 'clicked', 'completed-quiz'])
    clicked_count = sum(1 for r in campaign['recipients'] if r['status'] in ['clicked', 'completed-quiz'])
    quiz_count = sum(1 for r in campaign['recipients'] if r['status'] == 'completed-quiz')
    
    click_rate = clicked_count / sent_count if sent_count > 0 else 0
    quiz_completion_rate = quiz_count / clicked_count if clicked_count > 0 else 0
    
    # Update campaign metrics
    campaign['metrics'] = {
        'click_rate': click_rate,
        'quiz_completion_rate': quiz_completion_rate,
        'avg_quiz_score': sum(r.get('quiz_score', 0) for r in campaign['recipients'] if 'quiz_score' in r) / quiz_count if quiz_count > 0 else 0
    }
    st.session_state.campaigns[selected_campaign] = campaign
    save_campaigns()
    
    # Display metrics
    col1.metric("Sent", f"{sent_count}/{total_recipients}", f"{sent_count/total_recipients:.1%}")
    col2.metric("Clicked", f"{clicked_count}/{sent_count}", f"{click_rate:.1%}")
    col3.metric("Quiz Completed", f"{quiz_count}/{clicked_count}", f"{quiz_completion_rate:.1%}")
    
    # Timeline
    st.subheader("Campaign Timeline")
    st.write(f"**Created:** {campaign['created_at']}")
    st.write(f"**Status:** {campaign['status']}")
    
    # First click time
    first_click = min([r.get('click_ts', float('inf')) for r in campaign['recipients'] if 'click_ts' in r], default=None)
    if first_click and first_click != float('inf'):
        st.write(f"**First Click:** {datetime.fromtimestamp(first_click).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Recipient details
    st.subheader("Recipient Details")
    
    # Filter options
    status_filter = st.multiselect(
        "Filter by Status",
        options=['queued', 'sent', 'bounced', 'clicked', 'completed-quiz', 'failed'],
        default=['sent', 'clicked', 'completed-quiz']
    )
    
    # Filtered recipients
    filtered_recipients = [r for r in campaign['recipients'] if r['status'] in status_filter]
    
    # Display as table
    if filtered_recipients:
        import pandas as pd
        
        # Prepare data for table
        data = []
        for r in filtered_recipients:
            row = {
                'Email': r['email'],
                'Status': r['status'].capitalize(),
                'Sent Time': datetime.fromtimestamp(r.get('send_ts', 0)).strftime('%Y-%m-%d %H:%M:%S') if 'send_ts' in r else '-',
                'Click Time': datetime.fromtimestamp(r.get('click_ts', 0)).strftime('%Y-%m-%d %H:%M:%S') if 'click_ts' in r else '-',
                'Quiz Score': f"{r.get('quiz_score', 0)}/5" if 'quiz_score' in r else '-'
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        st.dataframe(df)
        
        # Export options
        col1, col2 = st.columns(2)
        if col1.button("Export as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"campaign_{selected_campaign}_report.csv",
                mime="text/csv"
            )
        
        if col2.button("Export as JSON"):
            json_data = json.dumps(campaign, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"campaign_{selected_campaign}_full.json",
                mime="application/json"
            )
    else:
        st.info("No recipients match the selected filters.")

# Settings page
def show_settings():
    st.title("Settings")
    
    # API Configuration
    st.subheader("API Configuration")
    
    with st.form("api_settings"):
        # Mailgun settings
        st.write("**Mailgun Settings**")
        mailgun_api_key = st.text_input("Mailgun API Key", type="password", value=os.environ.get("MAILGUN_API_KEY", ""))
        mailgun_domain = st.text_input("Mailgun Domain", value=os.environ.get("MAILGUN_DOMAIN", ""))
        sender_email = st.text_input("Default Sender Email", value=os.environ.get("DEFAULT_SENDER_EMAIL", ""))
        
        # LLM settings
        st.write("**LLM Settings**")
        llm_provider = st.selectbox("LLM Provider", ["OpenAI", "Google Gemini", "Anthropic"], index=0)
        
        if llm_provider == "OpenAI":
            openai_api_key = st.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
        elif llm_provider == "Google Gemini":
            gemini_api_key = st.text_input("Google Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
        elif llm_provider == "Anthropic":
            anthropic_api_key = st.text_input("Anthropic API Key", type="password", value=os.environ.get("ANTHROPIC_API_KEY", ""))
        
        # Application settings
        st.write("**Application Settings**")
        app_url = st.text_input("Application URL", value=os.environ.get("APP_URL", "https://phishing-trainer.streamlit.app"))
        debug_mode = st.checkbox("Debug Mode", value=os.environ.get("DEBUG_MODE", "False").lower() == "true")
        
        # Save settings
        if st.form_submit_button("Save Settings"):
            # In a real app, we would save these to .env or a secure config store
            # For this demo, we'll just show a success message
            st.success("Settings saved successfully!")
    
    # Danger Zone
    st.subheader("Danger Zone")
    with st.expander("Delete All Data"):
        st.warning("This will delete all campaigns and tracking data. This action cannot be undone.")
        confirm_delete = st.text_input("Type 'DELETE' to confirm", max_chars=6)
        if st.button("Delete All Data", disabled=(confirm_delete != "DELETE")):
            # Clear all data
            st.session_state.campaigns = {}
            save_campaigns()
            
            # Delete tracking data
            clicks_file = Path("data/clicks.json")
            if clicks_file.exists():
                clicks_file.unlink()
            
            st.success("All data has been deleted.")
            st.experimental_rerun()

# Helper function to clone a campaign
def clone_campaign(campaign_id):
    if campaign_id not in st.session_state.campaigns:
        return
    
    # Get the original campaign
    original = st.session_state.campaigns[campaign_id]
    
    # Create a new campaign with a new ID
    new_id = str(uuid.uuid4())
    new_campaign = original.copy()
    new_campaign['id'] = new_id
    new_campaign['name'] = f"Copy of {original['name']}"
    new_campaign['created_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_campaign['status'] = 'draft'
    
    # Reset recipient statuses
    for recipient in new_campaign['recipients']:
        recipient['id'] = str(uuid.uuid4())
        recipient['status'] = 'queued'
        if 'send_ts' in recipient:
            del recipient['send_ts']
        if 'click_ts' in recipient:
            del recipient['click_ts']
        if 'track_url' in recipient:
            del recipient['track_url']
    
    # Reset metrics
    new_campaign['metrics'] = {
        'click_rate': 0,
        'quiz_completion_rate': 0,
        'avg_quiz_score': 0
    }
    
    # Save the new campaign
    st.session_state.campaigns[new_id] = new_campaign
    save_campaigns()
    
    # Set as current campaign and navigate to edit
    st.session_state.current_campaign = new_id
    st.session_state.page = "create_campaign"

# Run the app
if __name__ == "__main__":
    main()