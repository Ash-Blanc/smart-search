#!/usr/bin/env python3
"""
Smart Search CLI - A lightweight command-line interface for the Smart Search engine.

This CLI provides fast, efficient access to the same AI-powered search capabilities
as the web interface, but with minimal overhead for power users and automation.
"""

import argparse
import sys
import json
from datetime import datetime
import hashlib

# Add parent directory to path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.personalization import PersonalizedSmartSearch

def create_user_id():
    """Create a unique user ID for tracking search history."""
    return hashlib.md5(
        str(datetime.now()).encode()
    ).hexdigest()[:8]

def main():
    parser = argparse.ArgumentParser(
        description="Smart Search - AI-powered search with zero hallucinations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  smart-search "Latest developments in quantum computing"
  smart-search "Climate change solutions" --depth deep --confidence 80
  smart-search "Python best practices" --format json --output results.json
        """
    )
    
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('-d', '--depth', choices=['quick', 'standard', 'deep'], 
                       default='standard', help='Search depth (default: standard)')
    parser.add_argument('-c', '--confidence', type=int, default=70,
                       help='Minimum confidence level (0-100, default: 70)')
    parser.add_argument('-f', '--format', choices=['text', 'json'], 
                       default='text', help='Output format (default: text)')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive mode')
    parser.add_argument('-u', '--user-id', default=None,
                       help='User ID for personalization (default: auto-generated)')
    parser.add_argument('--version', action='version', version='Smart Search CLI 0.1.0')
    
    args = parser.parse_args()
    
    # If no query and not in interactive mode, show help
    if not args.query and not args.interactive:
        parser.print_help()
        return
    
    # Initialize search system
    search_system = PersonalizedSmartSearch()
    
    # Use provided user ID or generate one
    user_id = args.user_id if args.user_id else create_user_id()
    
    if args.interactive:
        interactive_mode(search_system, user_id)
    else:
        # Single search mode
        result = execute_search(search_system, args.query, user_id, args.depth, args.confidence)
        output_result(result, args.format, args.output)

def interactive_mode(search_system, user_id):
    """Run the CLI in interactive mode."""
    print("🔍 Smart Search CLI - Interactive Mode")
    print("Type 'quit' or 'exit' to leave")
    print("-" * 40)
    
    while True:
        try:
            query = input("\nSearch: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
                
            print("Searching...")
            result = execute_search(search_system, query, user_id)
            
            # Display results
            print(f"\n📊 Confidence: {result['confidence']}%")
            if result.get('using_fallback'):
                print("⚠️  Using fallback LLM provider")
            print("-" * 40)
            print(result['results'])
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break

def execute_search(search_system, query, user_id, depth="standard", confidence=70):
    """Execute a search with the given parameters."""
    try:
        # Execute search
        result = search_system.search(query=query, user_id=user_id)
        
        # Apply confidence filter
        if result['confidence'] < confidence:
            result['results'] = f"⚠️  Low confidence result (confidence: {result['confidence']}%)\n\n{result['results']}"
        
        return result
    except Exception as e:
        return {
            'results': f"❌ Search failed: {str(e)}",
            'confidence': 0,
            'verification': 'Search error occurred'
        }

def output_result(result, format_type, output_file):
    """Output the result in the specified format."""
    if format_type == 'json':
        output_data = {
            'timestamp': datetime.now().isoformat(),
            'confidence': result['confidence'],
            'results': result['results'],
            'verification': result['verification'],
            'personalized': result.get('personalized', False),
            'using_fallback': result.get('using_fallback', False)
        }
        
        output_str = json.dumps(output_data, indent=2)
    else:  # text format
        output_str = f"""📊 Smart Search Result
===================

🔍 Confidence: {result['confidence']}%
{'⚠️  Using fallback LLM provider' if result.get('using_fallback') else ''}
{'👤 Personalized results' if result.get('personalized') else ''}

📄 Results:
{result['results']}

✅ Verification:
{result['verification']}
"""
    
    # Output to file or stdout
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_str)
            print(f"Results saved to {output_file}")
        except Exception as e:
            print(f"❌ Failed to write to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_str)

if __name__ == "__main__":
    main()