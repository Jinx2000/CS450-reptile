#!/usr/bin/env python3

import re
import csv
import argparse

def extract_links_from_content(content: str, base_url: str = None):
    """
    Extract all links from the text with [LINK:...] annotations and make them clickable.
    If a base URL is provided, prepend it to relative links (those starting with '/').
    
    Args:
        content (str): The text content containing [LINK:...] annotations.
        base_url (str): The base URL to prepend to relative links.

    Returns:
        - cleaned_content (str): The content with [LINK:...] annotations removed.
        - links (list): A list of extracted clickable links.
    """
    link_pattern = r"\[LINK:(.*?)\]"
    links = re.findall(link_pattern, content)  # Extract all links

    # Make links clickable by prepending the base URL for relative links
    if base_url:
        links = [
            link if link.startswith("http") else f"{base_url.rstrip('/')}{link}"
            for link in links
        ]

    cleaned_content = re.sub(link_pattern, "", content).strip()  # Remove [LINK:...] annotations
    return cleaned_content, links

def add_links_to_csv(input_csv: str, output_csv: str, base_url: str):
    """
    Reads the input CSV, extracts links from the 'content' column, makes them clickable,
    and adds them to the 'link to' column. Writes the updated rows to a new output CSV file.

    Args:
        input_csv (str): Path to the input CSV file.
        output_csv (str): Path to the output CSV file.
        base_url (str): Base URL to prepend to relative links.
    """
    updated_rows = []

    # Read the input CSV
    with open(input_csv, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames

        # Ensure 'link to' column exists in the output
        if "link to" not in fieldnames:
            fieldnames.append("link to")

        for row in reader:
            # Extract links from the 'content' column
            cleaned_content, links = extract_links_from_content(row["content"], base_url=base_url)
            row["content"] = cleaned_content  # Update the content with links removed
            row["link to"] = "\n".join(links)  # Add links to the 'link to' column
            updated_rows.append(row)

    # Write the updated rows to the output CSV
    with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract links from content and add them to the 'link to' column in a CSV.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output CSV file.")
    parser.add_argument("--base-url", type=str, required=True, help="Base URL to prepend to relative links.")
    args = parser.parse_args()

    # Process the CSV to add clickable links
    add_links_to_csv(args.input, args.output, args.base_url)
