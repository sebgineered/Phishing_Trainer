"""Utility functions for the Standard Agent Prompts application.

This module provides helper functions for verifying, testing, and managing prompts
for Jentic's Standard Agent.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Mock implementation for demonstration purposes
# In a real application, this would use the Jentic API
class StandardAgentClient:
    """Mock client for interacting with Jentic's Standard Agent API."""
    
    def __init__(self, api_key: str = None):
        """Initialize the Standard Agent client.
        
        Args:
            api_key: The Jentic Agent API key
        """
        self.api_key = api_key or os.getenv("JENTIC_AGENT_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL", "gpt-4")
        self.connected = self._verify_connection()
    
    def _verify_connection(self) -> bool:
        """Verify the connection to the Jentic API.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        # In a real implementation, this would make an API call to verify the connection
        return self.api_key is not None and len(self.api_key) > 0
    
    def execute_prompt(self, prompt_text: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a prompt with the Standard Agent.
        
        Args:
            prompt_text: The prompt text to execute
            parameters: Optional parameters to include in the prompt
        
        Returns:
            Dict containing the execution results
        """
        # In a real implementation, this would make an API call to the Jentic Standard Agent
        # For demo purposes, we'll simulate a response
        
        if not self.connected:
            return {
                "success": False,
                "error": "Not connected to Jentic API. Please check your API key.",
                "execution_time": 0,
                "timestamp": datetime.now().isoformat(),
                "output": None
            }
        
        # Simulate API call delay
        time.sleep(1.5)
        
        # Format the prompt with parameters if provided
        formatted_prompt = prompt_text
        if parameters:
            try:
                formatted_prompt = prompt_text.format(**parameters)
            except KeyError as e:
                return {
                    "success": False,
                    "error": f"Missing parameter in prompt: {e}",
                    "execution_time": 0.1,
                    "timestamp": datetime.now().isoformat(),
                    "output": None
                }
        
        # Simulate success or failure (90% success rate)
        import random
        success = random.random() > 0.1
        
        if success:
            # Generate a mock response based on the prompt type
            output = self._generate_mock_output(formatted_prompt)
            execution_time = round(random.uniform(0.5, 5.0), 2)
            
            return {
                "success": True,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
                "output": output
            }
        else:
            # Simulate different types of errors
            errors = [
                "API rate limit exceeded",
                "Service temporarily unavailable",
                "Invalid parameter format",
                "Authentication error",
                "Timeout while processing request"
            ]
            error = random.choice(errors)
            
            return {
                "success": False,
                "error": error,
                "execution_time": round(random.uniform(0.1, 1.0), 2),
                "timestamp": datetime.now().isoformat(),
                "output": None
            }
    
    def _generate_mock_output(self, prompt: str) -> str:
        """Generate a mock output based on the prompt.
        
        Args:
            prompt: The formatted prompt text
        
        Returns:
            str: A mock output response
        """
        # Simple keyword-based response generation
        if "weather" in prompt.lower():
            return "Current weather in the requested location:\n- Temperature: 18°C\n- Conditions: Partly cloudy\n- Humidity: 65%\n\nForecast for the next 24 hours:\n- Tonight: Clear skies, 12°C\n- Tomorrow: Sunny with occasional clouds, 16-20°C"
        
        elif "research" in prompt.lower() or "papers" in prompt.lower() or "academic" in prompt.lower():
            return "Found 3 recent research papers on the requested topic:\n\n1. **Latest Advances in the Field**\n   - Authors: Smith, J., Johnson, M.\n   - Published: May 2023\n   - Summary: This paper presents new findings that advance the understanding of key mechanisms in the field.\n\n2. **Comparative Analysis of Methodologies**\n   - Authors: Williams, A., Brown, T.\n   - Published: April 2023\n   - Summary: The authors compare different approaches and identify optimal methodologies for various scenarios.\n\n3. **Future Directions and Challenges**\n   - Authors: Garcia, L., Zhang, Y.\n   - Published: March 2023\n   - Summary: This review paper outlines emerging trends and identifies key challenges that need to be addressed in future research."
        
        elif "news" in prompt.lower() or "articles" in prompt.lower():
            return "Latest news articles on the requested topic:\n\n1. **Major Development Announced**\n   - Source: New York Times\n   - Published: Yesterday\n   - Summary: A significant announcement has been made that could impact the future direction of this field.\n\n2. **Analysis of Recent Trends**\n   - Source: Washington Post\n   - Published: 2 days ago\n   - Summary: Experts analyze the patterns emerging in recent months and what they might mean going forward.\n\n3. **Interview with Leading Expert**\n   - Source: BBC News\n   - Published: 3 days ago\n   - Summary: An in-depth conversation with a prominent figure in the field, discussing current state and future prospects."
        
        elif "translate" in prompt.lower() or "yoda" in prompt.lower():
            return "Translated text:\n\n'Looking forward to meeting you tomorrow, I am. At the new restaurant downtown, lunch we will have. Hmmmm.'"
        
        elif "github" in prompt.lower() or "issues" in prompt.lower():
            return "Recent GitHub issues from the requested repository:\n\n1. #42: 'Add support for custom authentication' [enhancement]\n2. #39: 'Fix bug in data processing module' [bug, priority-high]\n3. #36: 'Improve error handling' [enhancement]\n4. #35: 'Update documentation' [documentation]\n5. #31: 'Add new feature' [feature, priority-medium]"
        
        else:
            return "I've processed your request and completed the task successfully. Here are the results based on your specifications."


def verify_setup() -> Dict[str, bool]:
    """Verify that the environment is properly set up for using the Standard Agent.
    
    Returns:
        Dict containing verification results for different components
    """
    results = {
        "env_variables": False,
        "agent_connection": False,
        "api_access": False
    }
    
    # Check environment variables
    required_vars = ["JENTIC_AGENT_API_KEY"]
    optional_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "LLM_MODEL"]
    
    # Check if at least one required var is set
    results["env_variables"] = any(os.getenv(var) for var in required_vars)
    
    # Check agent connection
    client = StandardAgentClient()
    results["agent_connection"] = client.connected
    
    # If connected, verify API access with a simple test
    if client.connected:
        test_result = client.execute_prompt("Test connection to Jentic API")
        results["api_access"] = test_result.get("success", False)
    
    return results


def test_prompt(prompt_data: Dict[str, Any], test_input: str = None) -> Dict[str, Any]:
    """Test a prompt with the Standard Agent.
    
    Args:
        prompt_data: The prompt data to test
        test_input: Optional test input to use instead of the example input
    
    Returns:
        Dict containing the test results
    """
    client = StandardAgentClient()
    
    if not client.connected:
        return {
            "success": False,
            "error": "Not connected to Jentic API. Please check your API key.",
            "execution_time": 0,
            "timestamp": datetime.now().isoformat(),
            "output": None
        }
    
    # Use the provided test input or fall back to the example input
    input_text = test_input or prompt_data.get("example_input", "")
    
    # Extract parameters from the input text based on the prompt template
    # This is a simplified implementation - in a real app, you'd need more sophisticated parsing
    parameters = {}
    prompt_text = prompt_data["prompt_text"]
    
    # Simple parameter extraction based on format placeholders
    import re
    format_params = re.findall(r'\{([^}]+)\}', prompt_text)
    
    # For demo purposes, we'll just use some default values
    # In a real implementation, you'd parse these from the input text
    default_values = {
        "location": "Dublin",
        "topic": "artificial intelligence",
        "email_address": "user@example.com",
        "text": "Hello, this is a test message.",
        "webhook_url": "https://discord.com/api/webhooks/example",
        "owner": "jentic",
        "repo": "standard-agent",
        "timezone": "EST",
        "message": "Your notification message",
        "learning_style": "visual",
        "resource_types": "videos, tutorials, books"
    }
    
    for param in format_params:
        parameters[param] = default_values.get(param, f"sample_{param}")
    
    # Execute the prompt
    result = client.execute_prompt(prompt_text, parameters)
    return result


def generate_performance_report(test_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a performance report based on test results.
    
    Args:
        test_results: Dictionary mapping prompt IDs to test results
    
    Returns:
        Dict containing the performance report
    """
    total_tests = len(test_results)
    successful_tests = sum(1 for result in test_results.values() if result.get("success", False))
    success_rate = round((successful_tests / max(total_tests, 1)) * 100, 2)
    
    avg_execution_time = 0
    if successful_tests > 0:
        execution_times = [result.get("execution_time", 0) for result in test_results.values() 
                          if result.get("success", False)]
        avg_execution_time = round(sum(execution_times) / max(len(execution_times), 1), 2)
    
    # Categorize errors
    error_categories = {}
    for result in test_results.values():
        if not result.get("success", False) and "error" in result:
            error = result["error"]
            error_categories[error] = error_categories.get(error, 0) + 1
    
    return {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "failed_tests": total_tests - successful_tests,
        "success_rate": success_rate,
        "avg_execution_time": avg_execution_time,
        "error_categories": error_categories,
        "timestamp": datetime.now().isoformat()
    }


def load_sample_prompts() -> List[Dict[str, Any]]:
    """Load sample prompts from the sample_prompts module.
    
    Returns:
        List of sample prompt dictionaries
    """
    try:
        from sample_prompts import SAMPLE_PROMPTS
        
        # Add IDs and timestamps if they don't exist
        for i, prompt in enumerate(SAMPLE_PROMPTS):
            if "id" not in prompt:
                prompt["id"] = f"sample_{i+1}"
            if "created_at" not in prompt:
                prompt["created_at"] = datetime.now().isoformat()
        
        return SAMPLE_PROMPTS
    except ImportError:
        # If sample_prompts.py doesn't exist, return an empty list
        return []


def save_prompts_to_file(prompts: List[Dict[str, Any]], filename: str = "saved_prompts.json") -> bool:
    """Save prompts to a JSON file.
    
    Args:
        prompts: List of prompt dictionaries to save
        filename: Name of the file to save to
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            json.dump(prompts, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving prompts: {e}")
        return False


def load_prompts_from_file(filename: str = "saved_prompts.json") -> List[Dict[str, Any]]:
    """Load prompts from a JSON file.
    
    Args:
        filename: Name of the file to load from
    
    Returns:
        List of prompt dictionaries
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading prompts: {e}")
        return []