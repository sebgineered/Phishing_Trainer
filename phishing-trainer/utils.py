import streamlit as st

# Generate a tracking URL (simplified)
def generate_tracking_url(campaign_id, recipient_id):
    base_url = "http://localhost:8501/track"
    return f"{base_url}?cid={campaign_id}&rid={recipient_id}"
