#!/usr/bin/env python3

import re
import csv
import argparse

CHUNK_PATTERN = re.compile(
    r"(===== CONCEPT CHUNK #\d+ =====.*?========================================)",
    re.DOTALL
)

def extract_links_from_content(content: str, base_url: str):
    """
    Extract all links from the text with [LINK:...] annotations and make them clickable.
    If a base URL is provided, prepend it to relative links (those starting with '/').
    """
    link_pattern = r"\[LINK:(.*?)\]"
    links = re.findall(link_pattern, content)

    # Prepend base URL for relative links
    clickable_links = [
        link if link.startswith("http") else f"{base_url.rstrip('/')}{link}" for link in links
    ]

    cleaned_content = re.sub(link_pattern, "", content).strip()  # Remove link annotations
    return cleaned_content, clickable_links

def parse_chunk(chunk_text: str, category: str, topic: str, base_url: str):
    """
    Parse a CONCEPT CHUNK to extract fields for the CSV:
        - Concept: H2 heading text
        - Content: Cleaned content including code blocks
        - URL: Base URL combined with the ID from H2
        - Link to: Extracted clickable links
    """
    # Extract Concept (H2 heading text) and ID
    concept_match = re.search(r"\[Concept:\s*(.*?)\s*\[id:\s*(.*?)\]\]", chunk_text)
    concept = concept_match.group(1).strip() if concept_match else "Unknown Concept"
    concept_id = concept_match.group(2).strip() if concept_match else ""

    # Extract Content
    content_start = chunk_text.find("Content:")
    content = chunk_text[content_start + len("Content:"):].strip() if content_start != -1 else ""
    content, links = extract_links_from_content(content, base_url)

    # Generate URL for the concept
    url = f"{base_url.rstrip('/')}/#{concept_id}" if concept_id else base_url

    return {
        "Category": category,
        "Topic": topic,
        "Concept": concept,
        "Content": content,
        "URL": url,
        "Link to": "\n".join(links),
        "Tag": "None"
    }

def process_file_to_csv(input_file: str, output_file: str, category: str, topic: str, base_url: str):
    """
    Processes the input text file into the new CSV format and writes the result to `output_file`.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        all_text = infile.read()

    # Extract all concept chunks
    chunks = CHUNK_PATTERN.findall(all_text)
    rows = [parse_chunk(chunk, category, topic, base_url) for chunk in chunks]

    # Write rows to the output CSV
    with open(output_file, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["ID", "Category", "Topic", "Concept", "Content", "URL", "Link to", "Tag"])
        writer.writeheader()

        for idx, row in enumerate(rows, start=1):
            row["ID"] = idx
            writer.writerow(row)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert processed CONCEPT CHUNK text to a CSV format.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input text file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output CSV file.")
    parser.add_argument("--category", type=str, required=True, help="Category name to assign to each document.")
    parser.add_argument("--topic", type=str, required=True, help="Topic (H1 text) to include in the CSV.")
    parser.add_argument("--base-url", type=str, required=True, help="Base URL for generating clickable links.")
    args = parser.parse_args()

    process_file_to_csv(args.input, args.output, args.category, args.topic, args.base_url)
