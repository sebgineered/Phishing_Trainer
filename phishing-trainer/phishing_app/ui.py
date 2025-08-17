"""
Defines the Streamlit user interface for the phishing simulator.

This module contains all the functions responsible for rendering the different
pages of the Streamlit application, including the dashboard, campaign creation,
reports, and settings pages. The main() function serves as the entry point
for the application.
"""

import asyncio
import logging
import uuid
from datetime import datetime

import pandas as pd
import streamlit as st

# Use absolute imports so that this module can be run directly by
# Streamlit without requiring a package context. Relative imports (e.g. `from .config import …`) only
# work when the module is imported as part of the `phishing_app` package.
# The package name is assumed to be ``phishing_app``, so we import the modules accordingly.
from phishing_app.config import (
    get_jentic_api_key,
    get_mailchimp_api_key,
    get_mailchimp_list_id,
    get_mailchimp_api_url,
    get_sender_email,
    save_settings,
)
from phishing_app.integration import JenticStandardAgent
from phishing_app.persistence import (
    generate_tracking_url,
    load_campaigns,
    save_campaigns,
    track_click_and_save,
)
from phishing_app.templates import generate_email_template, TEMPLATES
from phishing_app.utils import init_session_state, navigate_to, parse_targets


def configure_logging(debug_mode=False):
    """Configures the logging for the application."""
    level = logging.DEBUG if debug_mode else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def show_dashboard():
    """Renders the dashboard page."""
    st.title("Dashboard")
    
    if not st.session_state.campaigns:
        st.info("No campaigns yet. Create your first campaign!")
        st.button("Create Campaign", on_click=navigate_to, args=("create_campaign",))
        return
    
    st.subheader("Campaign Summary")
    
    col1, col2 = st.columns(2)
    
    total_campaigns = len(st.session_state.campaigns)
    total_targets = sum(len(campaign.get('recipients', [])) for campaign in st.session_state.campaigns.values())
    
    col1.metric("Total Campaigns", total_campaigns)
    col2.metric("Total Targets", total_targets)
    
    st.subheader("Recent Campaigns")
    
    for campaign_id, campaign in list(st.session_state.campaigns.items())[-5:]:
        with st.expander(f"{campaign['name']} ({campaign['created_at']})"):
            st.write(f"**Status:** {campaign['status']}")
            st.write(f"**Targets:** {len(campaign['recipients'])}")
            
            col1, col2 = st.columns(2)
            col1.button(f"View Report #{campaign_id}", key=f"report_{campaign_id}", 
                      on_click=lambda cid=campaign_id: (setattr(st.session_state, 'current_campaign', cid), navigate_to("reports")))


def show_create_campaign():
    """Renders the campaign creation page."""
    st.title("Create Phishing Campaign")
    
    with st.form("campaign_form"):
        st.subheader("Campaign Details")
        campaign_name = st.text_input("Campaign Name", placeholder="MS365-Verification-Aug16")
        
        st.subheader("Target Selection")
        target_emails = st.text_area("Target Emails (one per line)", placeholder="user1@example.com\nuser2@example.com")
        
        st.subheader("Phishing Scenario")
        company_name = st.text_input("Company/Brand Name", placeholder="Microsoft")
        
        scenario_type = st.selectbox("Scenario Type", list(TEMPLATES.keys()))
        
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted:
            if not campaign_name or not company_name:
                st.error("Campaign name and company name are required.")
                return
            
            validated_emails, invalid_emails = parse_targets(target_emails)

            if invalid_emails:
                st.warning(f"The following emails are invalid and will be skipped: {', '.join(invalid_emails)}")

            if not validated_emails:
                st.error("At least one valid target email is required.")
                return

            targets = [{'email': email, 'id': str(uuid.uuid4()), 'status': 'queued'} for email in validated_emails]
            
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
            
            email_content = generate_email_template(company_name, scenario_type)
            campaign['email_content'] = email_content
            
            for recipient in campaign['recipients']:
                recipient['track_url'] = generate_tracking_url(campaign_id, recipient['id'])
            
            st.session_state.campaigns[campaign_id] = campaign
            save_campaigns(st.session_state.campaigns)
            
            logging.info(f"Campaign '{campaign_name}' created successfully.")
            st.success(f"Campaign '{campaign_name}' created successfully!")
            st.session_state.current_campaign = campaign_id
            st.session_state.page = "email_preview"
            st.rerun()


def show_email_preview():
    """Renders the email preview page."""
    st.title("Email Preview")
    
    if not st.session_state.current_campaign or st.session_state.current_campaign not in st.session_state.campaigns:
        st.error("No campaign selected.")
        st.button("Back to Dashboard", on_click=navigate_to, args=("dashboard",))
        return
    
    campaign = st.session_state.campaigns[st.session_state.current_campaign]
    
    st.subheader(f"Campaign: {campaign['name']}")
    
    st.write("**Subject:**", campaign['email_content']['subject'])
    
    st.write("**Email Body:**")
    st.code(campaign['email_content']['body_html'], language="html")
    
    with st.expander("Edit Email Content"):
        new_subject = st.text_input("Subject", value=campaign['email_content']['subject'])
        new_body = st.text_area("Body HTML", value=campaign['email_content']['body_html'], height=300)
        
        if st.button("Update Email Content"):
            campaign['email_content']['subject'] = new_subject
            campaign['email_content']['body_html'] = new_body
            st.session_state.campaigns[st.session_state.current_campaign] = campaign
            save_campaigns(st.session_state.campaigns)
            st.success("Email content updated!")
    
    if st.button("Send Campaign"):
        jentic_agent = JenticStandardAgent()
        if not jentic_agent.connected:
            st.error("Jentic client not connected. Please check your API key in Settings.")
            return

        with st.spinner("Sending emails..."):
            success_count = 0
            for recipient in campaign['recipients']:
                try:
                    sent, response = asyncio.run(jentic_agent.send_phishing_email(
                        campaign['company']['name'],
                        campaign['scenario']['type'],
                        recipient['email']
                    ))
                    if sent:
                        success_count += 1
                        recipient['status'] = 'sent'
                        recipient['send_ts'] = datetime.now().timestamp()
                        logging.info(f"Email sent to {recipient['email']}")
                    else:
                        logging.error(f"Failed to send email to {recipient['email']}. Response: {response}")
                        st.session_state.debug_info = {"status_code": response.status_code, "body": response.text}
                except Exception as e:
                    logging.error(f"An error occurred while sending email to {recipient['email']}: {e}")
                    st.session_state.debug_info = {"error": str(e)}

        campaign['status'] = 'active'
        st.session_state.campaigns[st.session_state.current_campaign] = campaign
        save_campaigns(st.session_state.campaigns)
        
        st.success(f"Campaign sent! {success_count}/{len(campaign['recipients'])} emails sent successfully.")
        st.button("View Reports", on_click=navigate_to, args=("reports",))


def show_reports():
    """Renders the campaign reports page."""
    st.title("Campaign Reports")
    
    if not st.session_state.campaigns:
        st.info("No campaigns available.")
        return
    
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
    
    st.subheader("Campaign Overview")
    st.write(f"**Name:** {campaign['name']}")
    st.write(f"**Created:** {campaign['created_at']}")
    st.write(f"**Status:** {campaign['status']}")
    st.write(f"**Company:** {campaign['company']['name']}")
    st.write(f"**Scenario:** {campaign['scenario']['type']}")
    
    st.subheader("Target Statistics")
    
    total = len(campaign['recipients'])
    sent = sum(1 for r in campaign['recipients'] if r['status'] == 'sent')
    clicked = sum(1 for r in campaign['recipients'] if r.get('click_ts') is not None)
    
    click_rate = (clicked / sent * 100) if sent > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Targets", total)
    col2.metric("Emails Sent", sent)
    col3.metric("Clicked Link", f"{clicked} ({click_rate:.1f}%)")
    
    st.subheader("Target Details")
    
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


def track_click():
    """Renders the phishing awareness page when a tracking link is clicked."""
    query_params = st.query_params
    campaign_id = query_params.get("cid", [""])[0]
    recipient_id = query_params.get("rid", [""])[0]
    
    if track_click_and_save(campaign_id, recipient_id):
        st.title("Phishing Awareness Training")
        st.warning("This was a simulated phishing test.")
        st.write("You clicked on a link in a phishing simulation email. In a real scenario, this could have led to:")
        st.write("- Credential theft")
        st.write("- Malware installation")
        st.write("- Account compromise")
        st.write("\nAlways verify the sender and be cautious of unexpected emails asking you to click links or provide information.")
    else:
        st.title("Invalid Link")
        st.error("This link is invalid or has expired.")


def show_settings():
    """Renders the settings page."""
    st.title("Settings")
    
    st.header("API Configuration")
    
    st.subheader("Jentic Integration")
    jentic_api_key = st.text_input(
        "Jentic Agent API Key", 
        value=get_jentic_api_key(),
        type="password",
        help="API key for Jentic's Standard Agent integration"
    )
    
    st.subheader("Email Service")
    mailchimp_api_key = st.text_input(
        "Mailchimp API Key", 
        value=get_mailchimp_api_key(),
        type="password",
        help="API key for Mailchimp email service (used by Jentic)"
    )
    
    sender_email = st.text_input(
        "Sender Email",
        value=get_sender_email(),
        help="Email address used as the sender for phishing simulations"
    )

    mailchimp_list_id = st.text_input(
        "Mailchimp List ID",
        value=get_mailchimp_list_id(),
        help="Required: Mailchimp Audience/List ID (found in Audience settings)"
    )
    
    if not mailchimp_list_id:
        st.warning("⚠️ Mailchimp List ID is required for sending emails")
    
    mailchimp_api_url = st.text_input(
        "Mailchimp API URL",
        value=get_mailchimp_api_url(),
        help="Mailchimp API endpoint URL"
    )
    
    st.subheader("Debugging")
    debug_mode = st.checkbox("Enable Debug Mode", value=st.session_state.get("debug_mode", False))
    if debug_mode != st.session_state.get("debug_mode"):
        st.session_state.debug_mode = debug_mode
        configure_logging(debug_mode)
        st.rerun()

    if st.session_state.get("debug_mode") and st.session_state.get('debug_info'):
        st.subheader("Last Jentic API Call")
        st.json(st.session_state.debug_info)
    
    if st.button("Save Settings"):
        settings = {
            "JENTIC_AGENT_API_KEY": jentic_api_key,
            "MAILCHIMP_API_KEY": mailchimp_api_key,
            "EMAIL_SENDER": sender_email,
            "MAILCHIMP_LIST_ID": mailchimp_list_id,
            "MAILCHIMP_DC": "us7",
            "MAILCHIMP_API_URL": mailchimp_api_url
        }
        save_settings(settings)
        st.success("Settings saved successfully to .env file!")
        st.info("Note: API keys are stored in the .env file in your project directory.")


def main():
    """Main function for the Streamlit application."""
    st.set_page_config(
        page_title="Basic Phishing Simulation",
        page_icon="🎣",
        layout="wide"
    )
    
    init_session_state()
    
    with st.sidebar:
        st.title("🎣 Phishing Trainer")
        st.button("Dashboard", on_click=navigate_to, args=("dashboard",))
        st.button("Create Campaign", on_click=navigate_to, args=("create_campaign",))
        st.button("Reports", on_click=navigate_to, args=("reports",))
        st.button("Settings", on_click=navigate_to, args=("settings",))
        
        st.divider()
        st.info("This is a basic phishing simulation tool for educational purposes only.")
    
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


if __name__ == "__main__":
    query_params = st.query_params
    if "cid" in query_params and "rid" in query_params:
        track_click()
    else:
        main()
