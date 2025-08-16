# Basic Phishing Simulation & Awareness Trainer

This is a simplified version of the Phishing Simulation & Awareness Trainer application. It provides the core functionality for creating phishing campaigns, generating emails, and tracking clicks.

## Features

- Create phishing campaigns with customizable scenarios
- Generate phishing emails based on templates
- Track email opens and link clicks
- View campaign reports and statistics

## Prerequisites

- Python 3.8 or higher
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository
2. Install the required packages:

```
pip install -r requirements.txt
```

## Running the Application

To run the basic version of the application:

```
streamlit run basic_app.py
```

This will start the Streamlit server and open the application in your default web browser.

## Usage

1. **Create a Campaign**: Fill in the campaign details, target emails, and select a phishing scenario.
2. **Preview Email**: Review and edit the generated email content.
3. **Simulate Send**: Simulate sending the campaign (in a real implementation, this would send actual emails).
4. **View Reports**: Check campaign statistics and track which recipients clicked on phishing links.

## Project Structure

- `basic_app.py`: Main application file with Streamlit UI and core functionality
- `data/`: Directory for storing campaign data
- `requirements.txt`: List of required Python packages

## Future Enhancements

This basic version can be extended with additional features:

- Integration with email sending services (Mailgun, SendGrid, etc.)
- Advanced email templates and customization
- Quiz functionality for clicked recipients
- Security checks for email content
- Domain validation and email safety features
- Advanced metrics and reporting dashboard

## Disclaimer

This tool is for educational purposes only. Always obtain proper authorization before conducting phishing simulations.