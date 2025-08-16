#!/usr/bin/env python
"""
Test script for the Standard Agent Prompts application.

This script tests all prompts in the collection and displays the results.
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
from prompt_utils import test_prompt, load_prompts_from_file, load_sample_prompts


def main():
    """Parse arguments and run tests for all prompts."""
    parser = argparse.ArgumentParser(description="Test all prompts with the Standard Agent")
    parser.add_argument(
        "--file", 
        help="Path to a JSON file containing saved prompts"
    )
    parser.add_argument(
        "--include-samples", 
        action="store_true",
        help="Include sample prompts in the test"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Display detailed output for each test"
    )
    
    args = parser.parse_args()
    
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
        print("\n❌ No prompts found to test")
        return
    
    print(f"\n🔍 Testing {len(prompts)} prompts...\n")
    
    # Test each prompt
    results = {}
    for i, prompt in enumerate(prompts):
        prompt_name = prompt.get("name", f"Prompt {i+1}")
        prompt_id = prompt.get("id", f"prompt_{i+1}")
        
        print(f"Testing {i+1}/{len(prompts)}: {prompt_name}...")
        
        result = test_prompt(prompt)
        results[prompt_id] = result
        
        # Display result if verbose
        if args.verbose:
            status = "✅ Success" if result.get("success", False) else "❌ Failed"
            print(f"  {status} - Execution time: {result.get('execution_time', 0)}s")
            if not result.get("success", False) and "error" in result:
                print(f"  Error: {result['error']}")
            print()
    
    # Display summary
    successful = sum(1 for r in results.values() if r.get("success", False))
    print(f"\n✅ {successful}/{len(results)} prompts tested successfully")
    
    # Generate performance report
    from prompt_utils import generate_performance_report
    report = generate_performance_report(results)
    
    print("\nPerformance Report:")
    print(f"  Success Rate: {report['success_rate']}%")
    print(f"  Average Execution Time: {report['avg_execution_time']}s")
    
    if report['error_categories']:
        print("\nError Categories:")
        for error, count in report['error_categories'].items():
            print(f"  {error}: {count} occurrences")
    
    # Save results to file
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    with open(filename, "w") as f:
        json.dump({
            "results": results,
            "report": report
        }, f, indent=2)
    
    print(f"\nDetailed results saved to {filename}")


if __name__ == "__main__":
    main()