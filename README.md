# Phishing Simulation & Awareness Trainer

## Overview
This application automatically generates realistic phishing emails, delivers them to test users, tracks interactions, and provides tailored awareness training. It leverages Jentic's Standard Agent for secure API handling and Arazzo workflows for multi-step simulations.

## Features
- Realistic phishing email generation using language models
- Secure email delivery via SendGrid integration
- Interaction tracking for clicks and form submissions
- Automated training content delivery based on user interactions
- Streamlit-based dashboard for campaign management and reporting

## Project Structure
- `agent-comms/`: Main application directory
  - `app.py`: Streamlit application entry point
  - `config.py`: Configuration management
  - `integrations/`: Communication classes for different platforms
    - `email_agent.py`: Email integration with Jentic
  - `models/`: Data models and schemas
    - `campaign.py`: Data models for campaigns, templates, and targets
  - `services/`: Business logic services
    - `phishing_generator.py`: Phishing email content generation
    - `training_service.py`: Training content delivery
  - `utils/`: Utility functions and helpers
    - `tracking.py`: Tracking link generation and click recording
    - `logger.py`: Logging configuration

## Setup
1. Create a virtual environment: `python -m venv .venv`
2. Activate the environment: 
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and fill in your API keys
5. Run the application: `cd agent-comms && streamlit run app.py`

## Implementation Details

### Email Integration
The application uses SendGrid for email delivery, with tracking capabilities for monitoring user interactions with phishing simulations.

### Phishing Content Generation
Phishing email content is generated using OpenAI's language models, with fallback templates available when API access is not available.

### Training Content
After users interact with phishing simulations, tailored training content is delivered based on the type of phishing attempt and user behavior.

### Security Considerations
- All API keys are stored securely using Jentic's vault
- Phishing emails are clearly marked as simulations in non-production environments
- Training content emphasizes ethical security awareness

## Jentic Integration
This project demonstrates Track 04 (Agent Comms) from the Jentic hackathon, focusing on email communication integration with Jentic's Standard Agent.