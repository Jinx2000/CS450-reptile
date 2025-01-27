#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup

def annotate_links_in_html(html_content: str) -> str:
    """
    Replace <a> tags with their inner text followed by a [LINK:href] annotation.
    Example:
        Input: <a href="https://example.com">Example</a>
        Output: Example [LINK:https://example.com]
    """
    soup = BeautifulSoup(html_content, "html.parser")
    for link in soup.find_all("a"):
        # Extract the inner text and href
        inner_text = link.get_text()
        href = link.get("href", "")
        # Replace <a> tag with 'inner_text [LINK:href]'
        annotated_text = f"{inner_text} [LINK:{href}]" if href else inner_text
        link.replace_with(annotated_text)
    return str(soup)

def main(input_file: str, output_file: str):
    """
    Reads HTML content from 'input_file', annotates <a> tags with [LINK:href],
    and writes the annotated content to 'output_file'.
    """
    # Read the input text (HTML content) from file
    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Annotate links in the HTML content
    annotated_content = annotate_links_in_html(html_content)

    # Write the annotated result to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(annotated_content)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Annotate <a> tags in HTML with [LINK:href].")
    parser.add_argument("--input", type=str, required=True, help="Path to the input HTML file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output annotated HTML file.")
    args = parser.parse_args()

    # Run the link annotation process
    main(args.input, args.output)
