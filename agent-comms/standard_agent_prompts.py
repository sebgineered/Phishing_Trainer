import streamlit as st
import os
import sys
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Standard Agent Prompts",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing prompts
if 'prompts' not in st.session_state:
    st.session_state.prompts = []

if 'test_results' not in st.session_state:
    st.session_state.test_results = {}

# Sidebar navigation
st.sidebar.title("Standard Agent Prompts")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Create Prompt", "Test Prompts", "Prompt Library", "Documentation", "Settings"]
)

# Helper functions
def save_prompt(prompt_data):
    """Save a prompt to the session state"""
    if 'id' not in prompt_data:
        # Generate a simple ID based on timestamp
        prompt_data['id'] = str(int(datetime.now().timestamp()))
        prompt_data['created_at'] = datetime.now().isoformat()
        st.session_state.prompts.append(prompt_data)
    else:
        # Update existing prompt
        for i, prompt in enumerate(st.session_state.prompts):
            if prompt['id'] == prompt_data['id']:
                st.session_state.prompts[i] = prompt_data
                break

def delete_prompt(prompt_id):
    """Delete a prompt from the session state"""
    st.session_state.prompts = [p for p in st.session_state.prompts if p['id'] != prompt_id]
    if prompt_id in st.session_state.test_results:
        del st.session_state.test_results[prompt_id]

def simulate_test_prompt(prompt_id, prompt_text):
    """Simulate testing a prompt with the Jentic Standard Agent"""
    # In a real implementation, this would call the Jentic API
    # For demo purposes, we'll simulate a successful test
    import time
    import random
    
    # Simulate API call delay
    time.sleep(1.5)
    
    # Simulate success or failure
    success = random.random() > 0.2  # 80% success rate
    
    result = {
        "success": success,
        "execution_time": round(random.uniform(0.5, 5.0), 2),
        "timestamp": datetime.now().isoformat(),
        "output": "Sample output from the Standard Agent" if success else "Error: API rate limit exceeded"
    }
    
    st.session_state.test_results[prompt_id] = result
    return result

# Main content based on selected page
if page == "Dashboard":
    st.title("Standard Agent Prompts Dashboard")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Prompts", value=len(st.session_state.prompts))
    with col2:
        successful_tests = sum(1 for result in st.session_state.test_results.values() if result.get('success', False))
        st.metric(label="Successful Tests", value=successful_tests)
    with col3:
        test_count = len(st.session_state.test_results)
        success_rate = f"{round(successful_tests / max(test_count, 1) * 100)}%"
        st.metric(label="Success Rate", value=success_rate)
    
    # Recent prompts
    st.subheader("Recent Prompts")
    if st.session_state.prompts:
        # Sort prompts by creation time (newest first)
        recent_prompts = sorted(
            st.session_state.prompts, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )[:5]
        
        for prompt in recent_prompts:
            with st.expander(f"{prompt['name']} ({prompt['api_category']})"):
                st.write(f"**Purpose:** {prompt['purpose']}")
                st.write(f"**Prompt:** {prompt['prompt_text']}")
                st.write(f"**APIs Used:** {', '.join(prompt['apis_used'])}")
                
                # Show test result if available
                if prompt['id'] in st.session_state.test_results:
                    result = st.session_state.test_results[prompt['id']]
                    status = "✅ Success" if result['success'] else "❌ Failed"
                    st.write(f"**Last Test:** {status} ({result['execution_time']}s)")
    else:
        st.info("No prompts created yet. Start by creating a new prompt.")

elif page == "Create Prompt":
    st.title("Create Standard Agent Prompt")
    
    # Prompt creation form
    with st.form("prompt_form"):
        name = st.text_input("Prompt Name", placeholder="E.g., Weather Information Retrieval")
        
        purpose = st.text_area(
            "Purpose", 
            placeholder="Describe what this prompt accomplishes"
        )
        
        api_category = st.selectbox(
            "API Category",
            ["Information Retrieval", "Content Generation", "Data Analysis", "Communication", "Multi-API Workflow"]
        )
        
        apis_used = st.multiselect(
            "APIs Used",
            ["Weather", "News", "Academic Papers", "Discord", "Email", "Translation", 
             "Figshare", "NYT", "Twitter/X", "GitHub", "Google Search", "Wikipedia"]
        )
        
        prompt_text = st.text_area(
            "Prompt Text", 
            placeholder="Enter the actual prompt text that will be sent to the Standard Agent",
            height=150
        )
        
        expected_time = st.slider("Expected Execution Time (seconds)", 1, 120, 30)
        
        example_input = st.text_area(
            "Example Input", 
            placeholder="Sample user request that would trigger this prompt"
        )
        
        example_output = st.text_area(
            "Expected Output", 
            placeholder="What the agent should return"
        )
        
        edge_cases = st.text_area(
            "Edge Cases", 
            placeholder="Known limitations or failure modes"
        )
        
        variations = st.text_area(
            "Variations", 
            placeholder="Alternative phrasings or parameters"
        )
        
        submitted = st.form_submit_button("Save Prompt")
        
        if submitted:
            if not name or not prompt_text or not purpose or not apis_used:
                st.error("Please fill in all required fields: Name, Purpose, APIs Used, and Prompt Text.")
            else:
                prompt_data = {
                    "name": name,
                    "purpose": purpose,
                    "api_category": api_category,
                    "apis_used": apis_used,
                    "prompt_text": prompt_text,
                    "expected_time": expected_time,
                    "example_input": example_input,
                    "example_output": example_output,
                    "edge_cases": edge_cases,
                    "variations": variations
                }
                
                save_prompt(prompt_data)
                st.success(f"Prompt '{name}' saved successfully!")

elif page == "Test Prompts":
    st.title("Test Standard Agent Prompts")
    
    if not st.session_state.prompts:
        st.info("No prompts available for testing. Please create a prompt first.")
    else:
        # Select prompt to test
        prompt_options = {p["name"]: p["id"] for p in st.session_state.prompts}
        selected_prompt_name = st.selectbox("Select Prompt to Test", list(prompt_options.keys()))
        selected_prompt_id = prompt_options[selected_prompt_name]
        
        # Find the selected prompt
        selected_prompt = next((p for p in st.session_state.prompts if p["id"] == selected_prompt_id), None)
        
        if selected_prompt:
            st.subheader("Prompt Details")
            st.write(f"**Purpose:** {selected_prompt['purpose']}")
            st.write(f"**APIs Used:** {', '.join(selected_prompt['apis_used'])}")
            
            # Display the prompt text
            st.text_area("Prompt Text", selected_prompt['prompt_text'], height=100, disabled=True)
            
            # Test parameters
            st.subheader("Test Parameters")
            test_input = st.text_area(
                "Test Input", 
                selected_prompt.get('example_input', ''),
                help="You can modify the input parameters for this test"
            )
            
            # Test button
            if st.button("Run Test"):
                with st.spinner("Testing prompt with Standard Agent..."):
                    result = simulate_test_prompt(selected_prompt_id, test_input)
                
                # Display test results
                st.subheader("Test Results")
                if result["success"]:
                    st.success("Test completed successfully!")
                else:
                    st.error("Test failed. See details below.")
                
                st.write(f"**Execution Time:** {result['execution_time']} seconds")
                st.write(f"**Timestamp:** {result['timestamp']}")
                st.text_area("Output", result['output'], height=150, disabled=True)
            
            # Show previous test results if available
            if selected_prompt_id in st.session_state.test_results and not st.button("Run Test"):
                st.subheader("Previous Test Results")
                prev_result = st.session_state.test_results[selected_prompt_id]
                status = "Success" if prev_result['success'] else "Failed"
                st.write(f"**Status:** {status}")
                st.write(f"**Execution Time:** {prev_result['execution_time']} seconds")
                st.write(f"**Timestamp:** {prev_result['timestamp']}")
                st.text_area("Output", prev_result['output'], height=150, disabled=True)

elif page == "Prompt Library":
    st.title("Prompt Library")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.multiselect(
            "Filter by Category",
            ["Information Retrieval", "Content Generation", "Data Analysis", "Communication", "Multi-API Workflow"],
            default=[]
        )
    with col2:
        filter_api = st.multiselect(
            "Filter by API",
            ["Weather", "News", "Academic Papers", "Discord", "Email", "Translation", 
             "Figshare", "NYT", "Twitter/X", "GitHub", "Google Search", "Wikipedia"],
            default=[]
        )
    
    # Display prompts
    if not st.session_state.prompts:
        st.info("No prompts in the library. Start by creating a new prompt.")
    else:
        # Apply filters
        filtered_prompts = st.session_state.prompts
        if filter_category:
            filtered_prompts = [p for p in filtered_prompts if p['api_category'] in filter_category]
        if filter_api:
            filtered_prompts = [p for p in filtered_prompts if any(api in p['apis_used'] for api in filter_api)]
        
        # Display filtered prompts
        if not filtered_prompts:
            st.warning("No prompts match the selected filters.")
        else:
            for prompt in filtered_prompts:
                with st.expander(f"{prompt['name']} ({prompt['api_category']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Purpose:** {prompt['purpose']}")
                        st.write(f"**Prompt:** {prompt['prompt_text']}")
                        st.write(f"**APIs Used:** {', '.join(prompt['apis_used'])}")
                        
                        if prompt.get('example_input'):
                            st.write(f"**Example Input:** {prompt['example_input']}")
                        
                        if prompt.get('example_output'):
                            st.write(f"**Example Output:** {prompt['example_output']}")
                    
                    with col2:
                        # Test status
                        if prompt['id'] in st.session_state.test_results:
                            result = st.session_state.test_results[prompt['id']]
                            status = "✅ Success" if result['success'] else "❌ Failed"
                            st.write(f"**Last Test:** {status}")
                            st.write(f"**Time:** {result['execution_time']}s")
                        else:
                            st.write("**Status:** Not tested")
                        
                        # Action buttons
                        if st.button("Test", key=f"test_{prompt['id']}"):
                            with st.spinner("Testing prompt..."):
                                result = simulate_test_prompt(prompt['id'], prompt.get('example_input', ''))
                            st.experimental_rerun()
                        
                        if st.button("Delete", key=f"delete_{prompt['id']}"):
                            delete_prompt(prompt['id'])
                            st.experimental_rerun()

elif page == "Documentation":
    st.title("Standard Agent Prompts Documentation")
    
    st.header("Getting Started")
    st.write("""
    This application helps you create, test, and verify high-quality prompts for Jentic's Standard Agent across different APIs and use cases.
    
    The Standard Agent can perform a wide range of tasks by combining different APIs and services. Your goal is to create prompts that demonstrate
    real-world use cases and showcase the capabilities of the Standard Agent.
    """)
    
    st.header("Prompt Types")
    st.subheader("1. Simple Single-API Prompts")
    st.write("""
    These prompts use one API to fetch and present information. Examples include:
    - Weather information queries
    - Academic paper searches
    - News article summaries
    - Translation requests
    """)
    
    st.subheader("2. Multi-API Workflow Prompts")
    st.write("""
    These prompts combine multiple APIs in sequence. Example patterns include:
    - Search → Summarize → Share: Find content, process it, distribute it
    - Translate → Format → Send: Process text and deliver via messaging
    - Fetch → Analyze → Report: Gather data and create formatted output
    """)
    
    st.subheader("3. Advanced Prompt Patterns")
    st.write("""
    These prompts maintain context across multiple interactions or make decisions based on data. Examples include:
    - "Remember my preferred news topics and find articles about them"
    - "If the weather is bad, suggest indoor activities, otherwise outdoor ones"
    - "Only send notifications during business hours"
    """)
    
    st.header("Testing Your Prompts")
    st.write("""
    For each prompt you create, verify that it:
    - Executes successfully with valid inputs
    - Handles errors gracefully with invalid inputs
    - Produces useful output that matches the request
    - Uses appropriate APIs for the task
    - Completes within reasonable time (< 2 minutes for most tasks)
    """)
    
    st.header("Documentation Template")
    st.code("""
    ## Prompt: [Brief Description]
    
    **Purpose**: What this prompt accomplishes
    **APIs Used**: List of APIs/services involved
    **Expected Time**: How long it typically takes
    **Example Input**: Sample user request
    **Example Output**: What the agent returns
    **Edge Cases**: Known limitations or failure modes
    **Variations**: Alternative phrasings or parameters
    """)

elif page == "Settings":
    st.title("Settings")
    
    st.header("API Configuration")
    
    # Jentic API settings
    st.subheader("Jentic API")
    jentic_api_key = st.text_input(
        "Jentic Agent API Key", 
        value=os.getenv("JENTIC_AGENT_API_KEY", ""),
        type="password"
    )
    
    # LLM Provider settings
    st.subheader("LLM Provider")
    llm_provider = st.selectbox(
        "LLM Provider",
        ["OpenAI", "Anthropic", "Google"],
        index=0
    )
    
    if llm_provider == "OpenAI":
        openai_api_key = st.text_input(
            "OpenAI API Key", 
            value=os.getenv("OPENAI_API_KEY", ""),
            type="password"
        )
        llm_model = st.selectbox(
            "Model",
            ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
    elif llm_provider == "Anthropic":
        anthropic_api_key = st.text_input(
            "Anthropic API Key", 
            value=os.getenv("ANTHROPIC_API_KEY", ""),
            type="password"
        )
        llm_model = st.selectbox(
            "Model",
            ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            index=1
        )
    elif llm_provider == "Google":
        google_api_key = st.text_input(
            "Google API Key", 
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password"
        )
        llm_model = st.selectbox(
            "Model",
            ["gemini-pro", "gemini-ultra"],
            index=0
        )
    
    # Additional API settings
    st.subheader("Additional API Credentials")
    st.write("Configure credentials for services you want to test (Discord, email, etc.)")
    
    with st.expander("Discord"):
        discord_webhook = st.text_input(
            "Discord Webhook URL", 
            value=os.getenv("DISCORD_WEBHOOK_URL", ""),
            type="password"
        )
    
    with st.expander("Email"):
        email_api_key = st.text_input(
            "Email API Key (SendGrid)", 
            value=os.getenv("SENDGRID_API_KEY", ""),
            type="password"
        )
        sender_email = st.text_input(
            "Sender Email", 
            value=os.getenv("SENDER_EMAIL", "")
        )
    
    # Save settings
    if st.button("Save Settings"):
        # In a real application, this would update the .env file or a database
        st.success("Settings saved successfully!")