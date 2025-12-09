#!/usr/bin/env python3
"""
Marketing Strategies HTML Parser
Parses marketing strategies from HTML file and outputs to JSON format.
Extracts strategy name, description, and funnel step types.
"""

import json
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any


def parse_marketing_strategies(html_file_path: str) -> List[Dict[str, Any]]:
    """
    Parse marketing strategies from HTML file.

    Args:
        html_file_path: Path to the HTML file containing marketing strategies

    Returns:
        List of dictionaries containing strategy information
    """
    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    strategies = []

    # Find all strategy containers
    # Each strategy is in a div with specific classes
    strategy_containers = soup.find_all('div', class_=lambda x: x and 'flex flex-col gap-3 rounded-' in x)

    for container in strategy_containers:
        try:
            # Extract strategy name
            name_elem = container.find('h3', class_='text-sm font-semibold')
            if not name_elem:
                continue

            strategy_name = name_elem.get_text(strip=True)

            # Extract description
            desc_elem = container.find('p', class_=lambda x: x and 'text-xs font-normal text-[#5A6A72]' in x)
            description = desc_elem.get_text(strip=True) if desc_elem else ""

            # Extract funnel steps/types
            funnel_steps = []
            funnel_elems = container.find_all('p', class_=lambda x: x and 'px-[0.35rem] py-[0.22rem] bg-[#D0E6FB]' in x)

            for elem in funnel_elems:
                step_text = elem.get_text(strip=True)
                if step_text and step_text != '+1':  # Skip the +1 indicators
                    funnel_steps.append(step_text)

            # Extract effort hours (optional metadata)
            effort_elem = container.find('p', class_=lambda x: x and 'text-[#5A6A72]' in x and 'hours' in x)
            effort_hours = None
            if effort_elem:
                hours_match = re.search(r'(\d+)\s*hours?', effort_elem.get_text(strip=True))
                if hours_match:
                    effort_hours = int(hours_match.group(1))

            # Extract impact level (optional metadata)
            impact_elem = container.find('span', class_=lambda x: x and 'bg-[#FFEEBE] text-[#AE8309]' in x)
            impact = impact_elem.get_text(strip=True) if impact_elem else None

            # Create strategy dictionary
            strategy = {
                'name': strategy_name,
                'description': description,
                'types': funnel_steps
            }

            # Add optional metadata if available
            if effort_hours is not None:
                strategy['effort_hours'] = effort_hours
            if impact:
                strategy['impact'] = impact

            strategies.append(strategy)

        except Exception as e:
            print(f"Error parsing strategy: {e}")
            continue

    return strategies


def main():
    """Main function to run the parser."""
    html_file = "marketing strategies.html"
    output_file = "marketing_strategies.json"

    try:
        # Parse strategies
        strategies = parse_marketing_strategies(html_file)

        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, indent=2, ensure_ascii=False)

        print(f"Successfully parsed {len(strategies)} marketing strategies")
        print(f"Output saved to {output_file}")

        # Print sample of first strategy
        if strategies:
            print("\nSample strategy:")
            print(json.dumps(strategies[0], indent=2, ensure_ascii=False))

    except FileNotFoundError:
        print(f"Error: File '{html_file}' not found")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
