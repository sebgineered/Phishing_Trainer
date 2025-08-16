import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import local modules
from integrations.email_agent import EmailAgent
from services.phishing_generator import PhishingGenerator
from services.training_service import TrainingService

# Page configuration
st.set_page_config(
    page_title="Phishing Simulation & Awareness Trainer",
    page_icon="🎣",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
email_agent = EmailAgent()
phishing_generator = PhishingGenerator()
training_service = TrainingService()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a page",
    ["Dashboard", "Create Campaign", "View Reports", "Settings"]
)

# Main content
st.title("Phishing Simulation & Awareness Trainer")

if page == "Dashboard":
    st.header("Dashboard")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active Campaigns", value="0")
    with col2:
        st.metric(label="Total Emails Sent", value="0")
    with col3:
        st.metric(label="Click Rate", value="0%")
    
    st.subheader("Recent Activity")
    st.info("No recent activity. Start by creating a new campaign.")

elif page == "Create Campaign":
    st.header("Create New Phishing Campaign")
    
    # Campaign form
    with st.form("campaign_form"):
        campaign_name = st.text_input("Campaign Name")
        target_group = st.text_input("Target Email Group")
        
        st.subheader("Phishing Email Configuration")
        template_type = st.selectbox(
            "Template Type",
            ["Password Reset", "Invoice Payment", "Document Review", "IT Notification", "Custom"]
        )
        
        difficulty = st.slider("Difficulty Level", 1, 5, 3)
        
        if template_type == "Custom":
            custom_template = st.text_area("Custom Template Content")
        
        st.subheader("Training Configuration")
        training_type = st.selectbox(
            "Training Type",
            ["Immediate Feedback", "Delayed Training", "Progressive Modules"]
        )
        
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted:
            st.success(f"Campaign '{campaign_name}' created successfully!")
            # Here we would call the actual campaign creation logic

elif page == "View Reports":
    st.header("Campaign Reports")
    st.info("No campaigns have been run yet. Reports will appear here after campaigns are executed.")

elif page == "Settings":
    st.header("Settings")
    
    st.subheader("Email Configuration")
    sender_email = st.text_input("Sender Email", value=os.getenv("EMAIL_SENDER", ""))
    
    st.subheader("API Keys")
    sendgrid_key = st.text_input("SendGrid API Key", value="********", type="password")
    jentic_key = st.text_input("Jentic API Key", value="********", type="password")
    openai_key = st.text_input("OpenAI API Key", value="********", type="password")
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")
        # Here we would save the settings to .env or a secure storage

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center;'>"
    "Powered by Jentic Standard Agent | "
    "<a href='https://github.com/your-repo/phishing-trainer' target='_blank'>GitHub</a>"
    "</div>",
    unsafe_allow_html=True
)