#!/usr/bin/env python
"""
Performance report generator for the Standard Agent Prompts application.

This script generates a detailed performance report for all prompts
tested with Jentic's Standard Agent.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import local modules
from prompt_utils import generate_performance_report, load_prompts_from_file, load_sample_prompts, test_prompt


def main():
    """Parse arguments and generate a performance report."""
    parser = argparse.ArgumentParser(description="Generate a performance report for Standard Agent prompts")
    parser.add_argument(
        "--file", 
        help="Path to a JSON file containing saved prompts"
    )
    parser.add_argument(
        "--results", 
        help="Path to a JSON file containing test results"
    )
    parser.add_argument(
        "--include-samples", 
        action="store_true",
        help="Include sample prompts in the report"
    )
    parser.add_argument(
        "--output", 
        help="Path to save the report (default: prompt_report_TIMESTAMP.md)"
    )
    parser.add_argument(
        "--retest", 
        action="store_true",
        help="Retest all prompts instead of using existing results"
    )
    
    args = parser.parse_args()
    
    # Load test results if available
    results = {}
    if args.results and not args.retest:
        try:
            with open(args.results, 'r') as f:
                data = json.load(f)
                if "results" in data:
                    results = data["results"]
                    print(f"Loaded test results from {args.results}")
                else:
                    print(f"Warning: No results found in {args.results}")
        except Exception as e:
            print(f"Error loading results: {e}")
    
    # Load prompts
    prompts = []
    
    # Load from file if specified
    if args.file:
        file_prompts = load_prompts_from_file(args.file)
        prompts.extend(file_prompts)
        print(f"Loaded {len(file_prompts)} prompts from {args.file}")
    else:
        # Default to saved_prompts.json
        file_prompts = load_prompts_from_file("saved_prompts.json")
        prompts.extend(file_prompts)
        print(f"Loaded {len(file_prompts)} prompts from saved_prompts.json")
    
    # Include sample prompts if requested
    if args.include_samples:
        sample_prompts = load_sample_prompts()
        prompts.extend(sample_prompts)
        print(f"Loaded {len(sample_prompts)} sample prompts")
    
    if not prompts:
        print("\n❌ No prompts found for the report")
        return
    
    # If we need to test the prompts
    if args.retest or not results:
        print(f"\n🔍 Testing {len(prompts)} prompts...\n")
        
        # Test each prompt
        results = {}
        for i, prompt in enumerate(prompts):
            prompt_name = prompt.get("name", f"Prompt {i+1}")
            prompt_id = prompt.get("id", f"prompt_{i+1}")
            
            print(f"Testing {i+1}/{len(prompts)}: {prompt_name}...")
            
            result = test_prompt(prompt)
            results[prompt_id] = result
            
            # Display brief result
            status = "✅ Success" if result.get("success", False) else "❌ Failed"
            print(f"  {status} - Execution time: {result.get('execution_time', 0)}s")
    
    # Generate performance report
    report = generate_performance_report(results)
    
    # Create markdown report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = args.output or f"prompt_report_{timestamp}.md"
    
    with open(output_file, "w") as f:
        f.write("# Standard Agent Prompts Performance Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Summary\n\n")
        f.write(f"- **Total Prompts Tested:** {report['total_tests']}\n")
        f.write(f"- **Successful Tests:** {report['successful_tests']} ({report['success_rate']}%)\n")
        f.write(f"- **Failed Tests:** {report['failed_tests']}\n")
        f.write(f"- **Average Execution Time:** {report['avg_execution_time']} seconds\n\n")
        
        if report['error_categories']:
            f.write("## Error Categories\n\n")
            for error, count in report['error_categories'].items():
                f.write(f"- **{error}:** {count} occurrences\n")
            f.write("\n")
        
        f.write("## Prompt Performance Details\n\n")
        f.write("| # | Prompt Name | Category | APIs Used | Success | Time (s) | Notes |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- |\n")
        
        for i, prompt in enumerate(prompts):
            prompt_id = prompt.get("id", f"prompt_{i+1}")
            name = prompt.get("name", "Unnamed")
            category = prompt.get("api_category", "N/A")
            apis = ", ".join(prompt.get("apis_used", ["N/A"]))
            
            if prompt_id in results:
                result = results[prompt_id]
                success = "✅" if result.get("success", False) else "❌"
                time = result.get("execution_time", "N/A")
                notes = result.get("error", "") if not result.get("success", False) else ""
            else:
                success = "⚠️"
                time = "N/A"
                notes = "Not tested"
            
            f.write(f"| {i+1} | {name} | {category} | {apis} | {success} | {time} | {notes} |\n")
        
        f.write("\n## Recommendations\n\n")
        
        # Add recommendations based on results
        if report['success_rate'] < 50:
            f.write("- **Critical:** The success rate is very low. Review API credentials and prompt formats.\n")
        elif report['success_rate'] < 80:
            f.write("- **Improvement Needed:** Several prompts are failing. Check error patterns and refine problematic prompts.\n")
        else:
            f.write("- **Good Performance:** Most prompts are working well. Focus on optimizing the few failing cases.\n")
        
        if report['avg_execution_time'] > 30:
            f.write("- **Performance Concern:** Average execution time is high. Consider simplifying complex prompts or breaking them into smaller steps.\n")
        
        # Add specific recommendations based on error categories
        if "API rate limit exceeded" in report['error_categories']:
            f.write("- **Rate Limiting:** Implement better rate limiting handling or request increased limits.\n")
        
        if "Authentication error" in report['error_categories']:
            f.write("- **Authentication:** Verify API keys and permissions for all services.\n")
    
    print(f"\n✅ Performance report generated: {output_file}")


if __name__ == "__main__":
    main()