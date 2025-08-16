#!/usr/bin/env python
"""
Verification script for the Standard Agent Prompts application.

This script checks that the environment is properly set up for using
Jentic's Standard Agent, including environment variables, API connections,
and access permissions.
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import local modules
from prompt_utils import verify_setup


def main():
    """Run the verification process and display results."""
    print("\n🔍 Verifying Standard Agent setup...\n")
    
    # Verify setup components
    results = verify_setup()
    
    # Display results
    if results["env_variables"]:
        print("✅ Environment variables configured")
    else:
        print("❌ Environment variables missing or incomplete")
        print("   Please check your .env file and ensure JENTIC_AGENT_API_KEY is set")
    
    if results["agent_connection"]:
        print("✅ Standard Agent connection working")
    else:
        print("❌ Could not connect to Standard Agent")
        print("   Please check your API key and internet connection")
    
    if results["api_access"]:
        print("✅ Jentic API access confirmed")
    else:
        print("❌ Could not access Jentic API")
        print("   Please check your API permissions")
    
    # Overall status
    if all(results.values()):
        print("\n🚀 Ready to create prompts!")
    else:
        print("\n⚠️ Setup incomplete. Please resolve the issues above before continuing.")


if __name__ == "__main__":
    main()