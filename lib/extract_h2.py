#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup

def extract_h2_sections(html_content: str):
    """
    Extract each <h2> in the given HTML and all content under it, 
    up to the next <h2> (or the end of the document).
    
    Returns a list where each element is a dictionary:
        {
            "title": the text of the <h2>,
            "content_html": all HTML content from after that <h2> 
                            until the next <h2>
        }
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all <h2> tags
    h2_tags = soup.find_all("h2")

    results = []

    # Loop through each <h2>
    for i, h2 in enumerate(h2_tags):
        section_title = h2.get_text(strip=True)  # the text content of the h2

        # We'll collect the content that follows this <h2>
        content_parts = []

        # Use next_sibling to iterate siblings until we find another <h2>
        node = h2.next_sibling

        while node:
            # If we encounter another <h2>, that means our current block ends
            if node.name == "h2":
                break
            # Otherwise, we collect it
            content_parts.append(str(node))
            node = node.next_sibling

        # Join everything into a single string
        section_content_html = "".join(content_parts).strip()

        # Add to results
        results.append({
            "title": section_title,
            "content_html": section_content_html
        })

    return results

def main(input_file, output_file):
    """
    Read HTML from input_file, extract <h2> sections, and write them to output_file.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    sections = extract_h2_sections(html_content)

    # Write the results as text to the output file.
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, sec in enumerate(sections, start=1):
            f.write(f"[{idx}] Category Title: {sec['title']}\n")
            f.write("Content:\n")
            f.write(sec["content_html"])
            f.write("\n\n" + "=" * 50 + "\n\n")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract <h2> sections and their content from HTML.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input HTML file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output text file.")
    args = parser.parse_args()

    # Run the main function
    main(args.input, args.output)
