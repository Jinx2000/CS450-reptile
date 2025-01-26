#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup

def remove_links_but_keep_text(html_content: str) -> str:
    """
    Remove all <a> tags from the HTML but keep the text that was inside them.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for link in soup.find_all("a"):
        # Replace the <a> tag with just its inner text
        link.replace_with(link.get_text())
    return str(soup)

def main(input_file: str, output_file: str):
    """
    Reads HTML content from 'input_file', removes all <a> tags while keeping their text,
    and writes the cleaned content to 'output_file'.
    """
    # Read the input text (HTML content) from file
    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Clean the HTML by removing <a> tags
    cleaned_content = remove_links_but_keep_text(html_content)

    # Write the cleaned result to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(cleaned_content)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Remove <a> tags from HTML while keeping their inner text.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input HTML file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output cleaned HTML file.")
    args = parser.parse_args()

    # Run the cleaning process
    main(args.input, args.output)
