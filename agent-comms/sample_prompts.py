"""Sample prompts for the Standard Agent Prompts application.

This module provides a collection of pre-defined prompts that demonstrate
the capabilities of Jentic's Standard Agent across different APIs and use cases.
"""

SAMPLE_PROMPTS = [
    {
        "name": "Weather Information Retrieval",
        "purpose": "Fetch current weather information for a specified location",
        "api_category": "Information Retrieval",
        "apis_used": ["Weather"],
        "prompt_text": "What's the current weather in {location}? Include temperature, conditions, and forecast for the next 24 hours.",
        "expected_time": 5,
        "example_input": "What's the current weather in Dublin, Ireland?",
        "example_output": "Current weather in Dublin, Ireland:\n- Temperature: 12°C\n- Conditions: Partly cloudy\n- Humidity: 78%\n\nForecast for the next 24 hours:\n- Tonight: Rain showers, 8°C\n- Tomorrow: Cloudy with occasional sun, 10-14°C",
        "edge_cases": "May fail with very obscure locations or during weather service outages",
        "variations": "What's the weather forecast for {location} this weekend?"
    },
    {
        "name": "Academic Paper Search",
        "purpose": "Find recent academic papers on a specific topic from Figshare",
        "api_category": "Information Retrieval",
        "apis_used": ["Academic Papers", "Figshare"],
        "prompt_text": "Find the latest 3 research papers on {topic} from Figshare. For each paper, provide the title, authors, publication date, and a brief summary.",
        "expected_time": 15,
        "example_input": "Find the latest 3 research papers on quantum computing from Figshare",
        "example_output": "Latest research papers on quantum computing from Figshare:\n\n1. **Quantum Error Correction in NISQ Devices**\n   - Authors: Zhang, L., Patel, K., & Johnson, M.\n   - Published: June 2023\n   - Summary: This paper presents a novel approach to quantum error correction that's suitable for current NISQ (Noisy Intermediate-Scale Quantum) devices, demonstrating a 23% improvement in qubit coherence time.\n\n2. **Variational Quantum Eigensolver Optimization**\n   - Authors: Sharma, P., & Williams, R.\n   - Published: May 2023\n   - Summary: The authors propose an enhanced optimization technique for the Variational Quantum Eigensolver algorithm that reduces the number of required measurements while maintaining accuracy.\n\n3. **Quantum Machine Learning for Financial Modeling**\n   - Authors: Chen, Y., Garcia, J., & Smith, T.\n   - Published: April 2023\n   - Summary: This paper explores the application of quantum machine learning algorithms to financial modeling, showing potential speedups for portfolio optimization problems.",
        "edge_cases": "May return fewer than 3 papers if the topic is very niche or new",
        "variations": "Find research papers on {topic} published in the last {timeframe}"
    },
    {
        "name": "News Summary and Email",
        "purpose": "Search for news articles on a topic, summarize them, and send via email",
        "api_category": "Multi-API Workflow",
        "apis_used": ["News", "NYT", "Email"],
        "prompt_text": "Search the New York Times for the latest articles about {topic}, create a brief summary of the top 3 articles, and email it to {email_address} with the subject 'News Update: {topic}'.",
        "expected_time": 30,
        "example_input": "Search the New York Times for the latest articles about climate change, create a brief summary of the top 3 articles, and email it to user@example.com with the subject 'News Update: Climate Change'.",
        "example_output": "I've searched for the latest articles about climate change from the New York Times, created summaries, and sent them to user@example.com.\n\nThe email contains summaries of these articles:\n1. "New UN Climate Report Warns of Accelerating Impacts"\n2. "European Union Unveils Ambitious Carbon Reduction Plan"\n3. "Climate Tech Investments Reach Record High in Q2"",
        "edge_cases": "May fail if email delivery is unsuccessful or if NYT API has usage limits",
        "variations": "Search for news about {topic} from {source}, summarize the most important developments, and send to {email_address}"
    },
    {
        "name": "Yoda Speak Translation",
        "purpose": "Translate text to Yoda-style speech and send via email",
        "api_category": "Content Generation",
        "apis_used": ["Translation", "Email"],
        "prompt_text": "Translate the following text to Yoda speak and send it via email to {email_address} with the subject 'Message from Yoda': {text}",
        "expected_time": 10,
        "example_input": "Translate the following text to Yoda speak and send it via email to user@example.com with the subject 'Message from Yoda': I am looking forward to meeting you tomorrow for lunch at the new restaurant downtown.",
        "example_output": "I've translated your message to Yoda speak and sent it to user@example.com.\n\nThe email contains:\n'Looking forward to meeting you tomorrow, I am. At the new restaurant downtown, lunch we will have. Hmmmm.'\n\nEmail delivered successfully.",
        "edge_cases": "Very technical or complex text may not translate well to Yoda speak",
        "variations": "Translate this message to {character} style and send it to {email_address}"
    },
    {
        "name": "Weather-Based Activity Suggestions",
        "purpose": "Check weather and suggest appropriate activities based on conditions",
        "api_category": "Advanced Prompt Patterns",
        "apis_used": ["Weather", "Google Search"],
        "prompt_text": "Check the current weather in {location}. If it's sunny and above 20°C, suggest outdoor activities. If it's rainy or below 10°C, suggest indoor activities. For anything in between, suggest a mix of both.",
        "expected_time": 15,
        "example_input": "Check the current weather in Boston. If it's sunny and above 20°C, suggest outdoor activities. If it's rainy or below 10°C, suggest indoor activities. For anything in between, suggest a mix of both.",
        "example_output": "Current weather in Boston:\n- Temperature: 15°C\n- Conditions: Partly cloudy\n\nSince the weather is mild (between 10-20°C), here are some activity suggestions:\n\nOutdoor Activities:\n1. Visit the Boston Public Garden\n2. Take a walk along the Freedom Trail\n3. Enjoy a coffee at an outdoor café (bring a light jacket)\n\nIndoor Activities:\n1. Explore the Museum of Fine Arts\n2. Visit the Boston Public Library\n3. Enjoy shopping at Faneuil Hall Marketplace\n\nThe weather is pleasant enough for outdoor activities but having indoor options is good in case clouds increase.",
        "edge_cases": "May not account for other weather factors like high winds or air quality",
        "variations": "What should I do today in {location} based on the weather forecast?"
    },
    {
        "name": "GitHub Issue Summary to Discord",
        "purpose": "Fetch recent GitHub issues from a repository and post summaries to Discord",
        "api_category": "Multi-API Workflow",
        "apis_used": ["GitHub", "Discord"],
        "prompt_text": "Get the 5 most recent open issues from the GitHub repository {owner}/{repo} and post a summary to the Discord channel using the webhook {webhook_url}. Include issue numbers, titles, and labels.",
        "expected_time": 20,
        "example_input": "Get the 5 most recent open issues from the GitHub repository jentic/standard-agent and post a summary to the Discord channel using the webhook https://discord.com/api/webhooks/example",
        "example_output": "I've fetched the 5 most recent open issues from jentic/standard-agent and posted them to Discord.\n\nThe following issues were included in the summary:\n1. #42: "Add support for custom API authentication" [enhancement, priority-medium]\n2. #39: "Fix rate limiting handling in weather API" [bug, priority-high]\n3. #36: "Improve error messages for failed API calls" [enhancement, documentation]\n4. #35: "Add unit tests for Discord integration" [test, priority-low]\n5. #31: "Update documentation for new API endpoints" [documentation]\n\nMessage successfully posted to Discord.",
        "edge_cases": "May fail if GitHub API rate limits are exceeded or if Discord webhook is invalid",
        "variations": "Summarize the pull requests for {owner}/{repo} created in the last week and post to Discord"
    },
    {
        "name": "Research Paper Summaries to Email",
        "purpose": "Find the latest AI research papers on Figshare and email summaries",
        "api_category": "Multi-API Workflow",
        "apis_used": ["Academic Papers", "Figshare", "Email"],
        "prompt_text": "Find the latest 3 AI research papers on Figshare and post summaries to {email_address}. Include titles, authors, publication dates, and brief summaries of each paper.",
        "expected_time": 45,
        "example_input": "Find the latest 3 AI research papers on Figshare and post summaries to user@example.com",
        "example_output": "I've found the latest 3 AI research papers on Figshare and sent summaries to user@example.com.\n\nThe email includes summaries of:\n1. "Advances in Transformer Architecture for Multi-modal Learning"\n2. "Ethical Considerations in Reinforcement Learning from Human Feedback"\n3. "Efficient Fine-tuning Methods for Large Language Models on Limited Hardware"\n\nEmail delivered successfully.",
        "edge_cases": "Results may vary based on what's recently been published on Figshare",
        "variations": "Find research papers about {topic} published in the last month and email summaries to {email_address}"
    },
    {
        "name": "Business Hours Notification",
        "purpose": "Send notifications only during business hours",
        "api_category": "Advanced Prompt Patterns",
        "apis_used": ["Email", "Discord"],
        "prompt_text": "Check the current time in {timezone}. If it's between 9 AM and 5 PM on a weekday, send the following message to {email_address}: {message}. Otherwise, schedule it to be sent at 9 AM on the next business day.",
        "expected_time": 10,
        "example_input": "Check the current time in EST. If it's between 9 AM and 5 PM on a weekday, send the following message to user@example.com: 'Your weekly report is ready for review.' Otherwise, schedule it to be sent at 9 AM on the next business day.",
        "example_output": "I checked the current time in EST: Tuesday, 2:30 PM (within business hours).\n\nI've sent the message 'Your weekly report is ready for review.' to user@example.com immediately.\n\nEmail delivered successfully.",
        "edge_cases": "May not account for holidays or company-specific business hours",
        "variations": "Send this notification to {recipient} only during their working hours based on their timezone {timezone}"
    },
    {
        "name": "Multi-source News Analysis",
        "purpose": "Gather news from multiple sources, analyze sentiment, and create a report",
        "api_category": "Data Analysis",
        "apis_used": ["News", "NYT", "Google Search"],
        "prompt_text": "Search for news about {topic} from the New York Times and at least 2 other major news sources. Analyze the sentiment (positive, negative, or neutral) of the coverage from each source and create a brief report comparing how different outlets are covering this topic.",
        "expected_time": 60,
        "example_input": "Search for news about artificial intelligence regulation from the New York Times and at least 2 other major news sources. Analyze the sentiment of the coverage from each source and create a brief report comparing how different outlets are covering this topic.",
        "example_output": "# News Coverage Analysis: Artificial Intelligence Regulation\n\n## Sources Analyzed\n1. New York Times\n2. Wall Street Journal\n3. BBC News\n\n## Sentiment Analysis\n\n**New York Times**: Primarily neutral with slightly negative tone (Sentiment score: -0.2)\n- Focuses on potential risks of unregulated AI\n- Emphasizes need for international cooperation\n- Quotes both industry leaders and critics\n\n**Wall Street Journal**: Slightly negative toward regulation (Sentiment score: -0.4)\n- Emphasizes potential economic impacts of strict regulation\n- Highlights industry self-regulation efforts\n- Features more business and industry perspectives\n\n**BBC News**: Neutral to slightly positive toward regulation (Sentiment score: +0.1)\n- More focus on European regulatory frameworks\n- Balanced coverage of risks and benefits\n- Includes more international perspectives\n\n## Key Differences\n- NYT provides the most comprehensive coverage of ethical concerns\n- WSJ emphasizes economic and innovation impacts more than other sources\n- BBC offers the most international perspective on regulatory approaches\n\n## Common Themes\n- All sources acknowledge the need for some form of AI oversight\n- All mention the challenges of regulating rapidly evolving technology\n- Recent EU AI Act is referenced across all sources\n\nThis analysis shows how media outlets frame AI regulation differently based on their typical audience and editorial perspective.",
        "edge_cases": "Analysis quality depends on the availability of recent articles on the topic",
        "variations": "Compare how {media_outlet_1} and {media_outlet_2} are covering {topic} and analyze the differences in their reporting"
    },
    {
        "name": "Personalized Learning Resource Finder",
        "purpose": "Find learning resources based on user's interests and learning style",
        "api_category": "Information Retrieval",
        "apis_used": ["Google Search", "Wikipedia"],
        "prompt_text": "Based on my interest in {topic} and preference for {learning_style} resources, find and recommend 3-5 high-quality learning resources. Include a mix of {resource_types} and explain why each resource would be valuable for me.",
        "expected_time": 30,
        "example_input": "Based on my interest in machine learning and preference for visual learning resources, find and recommend 3-5 high-quality learning resources. Include a mix of video courses, interactive tutorials, and books, and explain why each resource would be valuable for me.",
        "example_output": "# Personalized Machine Learning Resources for Visual Learners\n\n## 1. 3Blue1Brown Neural Network Video Series\n**Type**: Video Course (YouTube)\n**Link**: [Neural Networks](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi)\n**Why it's valuable**: Grant Sanderson's visual explanations of neural networks use beautiful animations to build intuition about how machine learning algorithms work. Perfect for visual learners who want to understand the mathematical foundations without getting lost in equations.\n\n## 2. Google's Machine Learning Playground\n**Type**: Interactive Tutorial\n**Link**: [Teachable Machine](https://teachablemachine.withgoogle.com/)\n**Why it's valuable**: This tool lets you create machine learning models right in your browser by training them with your webcam. The immediate visual feedback helps build intuition about how models learn from data.\n\n## 3. "Grokking Deep Learning" by Andrew Trask\n**Type**: Book with Visual Explanations\n**Link**: [Manning Publications](https://www.manning.com/books/grokking-deep-learning)\n**Why it's valuable**: Unlike many ML books, this one uses visual explanations and builds neural networks from scratch using only Python and NumPy. The author focuses on intuition and visualization before mathematics.\n\n## 4. Fast.ai Course\n**Type**: Video Course with Practical Projects\n**Link**: [Practical Deep Learning for Coders](https://course.fast.ai/)\n**Why it's valuable**: This course is known for its top-down approach, showing visual results first before diving into theory. The notebooks are filled with visualizations, and the teaching style emphasizes seeing models work before understanding all the details.\n\n## 5. TensorFlow Playground\n**Type**: Interactive Visualization\n**Link**: [TensorFlow Playground](https://playground.tensorflow.org/)\n**Why it's valuable**: This in-browser tool lets you visualize neural networks in real-time as they learn. You can adjust parameters and immediately see how they affect the learning process, making it perfect for visual learners.",
        "edge_cases": "Very niche topics may have limited high-quality visual resources available",
        "variations": "Find resources about {topic} suitable for someone with {background} and {time_available} to learn"
    }
]