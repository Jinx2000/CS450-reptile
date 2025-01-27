#!/usr/bin/env python3

import re
import csv
import argparse

def extract_links_from_content(content: str):
    """
    Extract all links from the text with [LINK:...] annotations.
    Returns:
        - cleaned_content: The content with [LINK:...] annotations removed.
        - links: A list of extracted links.
    """
    link_pattern = r"\[LINK:(.*?)\]"
    links = re.findall(link_pattern, content)  # Extract all links
    cleaned_content = re.sub(link_pattern, "", content).strip()  # Remove [LINK:...] annotations
    return cleaned_content, links

def add_links_to_csv(input_csv: str, output_csv: str):
    """
    Reads the input CSV, extracts links from the 'content' column, and adds them to the 'link to' column.
    Writes the updated rows to a new output CSV file.
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
            cleaned_content, links = extract_links_from_content(row["content"])
            row["content"] = cleaned_content  # Update the content with links removed
            row["link to"] = ", ".join(links)  # Add links to the 'link to' column
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
    args = parser.parse_args()

    # Process the CSV to add links
    add_links_to_csv(args.input, args.output)
