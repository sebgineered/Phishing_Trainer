# Phishing Simulation & Awareness Trainer

## Overview
This application automatically generates realistic phishing emails, delivers them to test users, tracks interactions, and provides tailored awareness training. It leverages Jentic's Standard Agent for secure API handling and Arazzo workflows for multi-step simulations.

## Features
- Realistic phishing email generation using language models
- Secure email delivery via SendGrid integration
- Interaction tracking for clicks and form submissions
- Automated training content delivery based on user interactions
- Streamlit-based dashboard for campaign management and reporting

## Setup
1. Clone this repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: 
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your API keys
6. Run the application: `streamlit run app.py`

## Project Structure
- `app.py`: Main Streamlit application entry point
- `integrations/`: Communication classes for different platforms
  - `email_agent.py`: Email integration with Jentic
- `models/`: Data models and schemas
- `services/`: Business logic services
  - `phishing_generator.py`: Phishing email content generation
  - `training_service.py`: Training content delivery
- `utils/`: Utility functions and helpers
- `config.py`: Configuration management

## Security Considerations
- All API keys are stored securely using Jentic's vault
- Phishing emails are clearly marked as simulations in non-production environments
- Training content emphasizes ethical security awareness