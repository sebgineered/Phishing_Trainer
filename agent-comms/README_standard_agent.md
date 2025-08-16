# Standard Agent Prompts

A collection of verified, working prompts that demonstrate the capabilities of Jentic's Standard Agent across different APIs and use cases.

## Overview

This application helps you create, test, and verify high-quality prompts for Jentic's Standard Agent. It provides a user-friendly interface for:

- Creating and managing prompts for different use cases
- Testing prompts with the Standard Agent
- Analyzing performance and success rates
- Documenting prompt patterns and best practices

## Features

- **Prompt Creation**: Build prompts with a structured template
- **Prompt Testing**: Test prompts with the Standard Agent and view results
- **Prompt Library**: Browse and filter a collection of prompts
- **Performance Analysis**: Generate reports on prompt success rates and execution times
- **Documentation**: Access guidelines and best practices for prompt creation

## Getting Started

### Prerequisites

- Python 3.11+
- Jentic Account with Agent API key
- LLM Provider (OpenAI, Anthropic, or Google) API key
- API credentials for services you want to test (Discord, email, etc.)

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:jentic/standard-agent.git
   cd standard-agent
   ```

2. Set up a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   ```bash
   cp .env.standard_agent.example .env
   # Edit .env with your API keys and credentials
   ```

5. Verify your setup:
   ```bash
   python verify_setup.py
   ```

### Running the Application

Start the Streamlit application:

```bash
streamlit run standard_agent_prompts.py
```

The application will be available at http://localhost:8501

## Prompt Types

### 1. Simple Single-API Prompts

These prompts use one API to fetch and present information. Examples include:
- Weather information queries
- Academic paper searches
- News article summaries
- Translation requests

### 2. Multi-API Workflow Prompts

These prompts combine multiple APIs in sequence. Example patterns include:
- Search → Summarize → Share: Find content, process it, distribute it
- Translate → Format → Send: Process text and deliver via messaging
- Fetch → Analyze → Report: Gather data and create formatted output

### 3. Advanced Prompt Patterns

These prompts maintain context across multiple interactions or make decisions based on data. Examples include:
- "Remember my preferred news topics and find articles about them"
- "If the weather is bad, suggest indoor activities, otherwise outdoor ones"
- "Only send notifications during business hours"

## Testing Your Prompts

### Using the UI

The application provides a testing interface where you can:
1. Select a prompt from your library
2. Modify test parameters if needed
3. Run the test and view results

### Using the Command Line

Test a single prompt:

```bash
python test_prompt.py "Find the latest AI research papers on Figshare"
```

Test a saved prompt by ID:

```bash
python test_prompt.py --id prompt_123
```

Test all prompts in your collection:

```bash
python test_all_prompts.py
```

Generate a performance report:

```bash
python prompt_performance_report.py
```

## Documentation Template

For each prompt, document:

```markdown
## Prompt: [Brief Description]

**Purpose**: What this prompt accomplishes
**APIs Used**: List of APIs/services involved
**Expected Time**: How long it typically takes
**Example Input**: Sample user request
**Example Output**: What the agent returns
**Edge Cases**: Known limitations or failure modes
**Variations**: Alternative phrasings or parameters
```

## Project Structure

```
.
├── standard_agent_prompts.py   # Main Streamlit application
├── prompt_utils.py            # Utility functions for prompt management
├── sample_prompts.py          # Collection of example prompts
├── verify_setup.py            # Setup verification script
├── test_prompt.py             # Script for testing individual prompts
├── test_all_prompts.py        # Script for testing all prompts
├── prompt_performance_report.py # Script for generating performance reports
├── .env.standard_agent.example # Example environment variables
└── README_standard_agent.md   # This documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.