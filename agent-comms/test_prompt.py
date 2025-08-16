#!/usr/bin/env python
"""
Test script for the Standard Agent Prompts application.

This script allows testing individual prompts with Jentic's Standard Agent
and displays the results.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import local modules
from prompt_utils import StandardAgentClient, test_prompt


def main():
    """Parse arguments and run the prompt test."""
    parser = argparse.ArgumentParser(description="Test a prompt with the Standard Agent")
    parser.add_argument(
        "prompt", 
        nargs="?", 
        help="The prompt text to test"
    )
    parser.add_argument(
        "--id", 
        help="The ID of a saved prompt to test"
    )
    parser.add_argument(
        "--file", 
        help="Path to a JSON file containing saved prompts"
    )
    
    args = parser.parse_args()
    
    # Check if we have a direct prompt text
    if args.prompt:
        print(f"\n🔍 Testing prompt: {args.prompt}\n")
        
        # Create a simple prompt data structure
        prompt_data = {
            "prompt_text": args.prompt,
            "example_input": args.prompt
        }
        
        # Test the prompt
        result = test_prompt(prompt_data)
        display_test_result(result)
    
    # Check if we have a prompt ID
    elif args.id:
        from prompt_utils import load_prompts_from_file
        
        # Load prompts from file
        filename = args.file or "saved_prompts.json"
        prompts = load_prompts_from_file(filename)
        
        # Find the prompt with the given ID
        prompt_data = next((p for p in prompts if p.get("id") == args.id), None)
        
        if prompt_data:
            print(f"\n🔍 Testing prompt: {prompt_data.get('name', 'Unnamed')}\n")
            result = test_prompt(prompt_data)
            display_test_result(result)
        else:
            print(f"\n❌ No prompt found with ID: {args.id}\n")
    
    # If no arguments provided, show usage
    else:
        parser.print_help()


def display_test_result(result):
    """Display the test result in a formatted way.
    
    Args:
        result: The test result dictionary
    """
    if result.get("success", False):
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    print(f"\nExecution Time: {result.get('execution_time', 0)} seconds")
    print(f"Timestamp: {result.get('timestamp', '')}")
    
    print("\nOutput:")
    print("-" * 80)
    print(result.get("output", "No output"))
    print("-" * 80)


if __name__ == "__main__":
    main()