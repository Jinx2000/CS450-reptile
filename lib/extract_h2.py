#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup

def extract_h1_and_h2_sections(html_content: str):
    """
    Extract the <h1> and each <h2> in the given HTML, along with content under each <h2>.

    Returns:
        - topic: The text content of the <h1> tag.
        - sections: A list where each element is a dictionary:
            {
                "title": The text of the <h2>,
                "id": The 'id' attribute of the <h2> (if exists),
                "content_html": All HTML content from after that <h2> 
                                until the next <h2>.
            }
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract <h1> tag
    h1_tag = soup.find("h1")
    topic = h1_tag.get_text(strip=True) if h1_tag else "Unknown Topic"

    # Find all <h2> tags
    h2_tags = soup.find_all("h2")

    sections = []

    # Loop through each <h2>
    for i, h2 in enumerate(h2_tags):
        section_title = h2.get_text(strip=True)  # The text content of the <h2>
        section_id = h2.get("id", "no-id")  # Get the 'id' attribute or default to 'no-id'

        # Collect the content that follows this <h2>
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

        # Add to sections
        sections.append({
            "title": section_title,
            "id": section_id,
            "content_html": section_content_html
        })

    return topic, sections

def main(input_file, output_file):
    """
    Read HTML from input_file, extract <h1> and <h2> sections, and write them to output_file.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Extract the topic and sections
    topic, sections = extract_h1_and_h2_sections(html_content)

    # Write the results as text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        # Write the topic at the top
        f.write(f"[TOPIC: {topic}]\n\n")

        # Write each <h2> section
        for idx, sec in enumerate(sections, start=1):
            f.write(f"[{idx}] Concept: {sec['title']} [id: {sec['id']}]\n")
            f.write("Content:\n")
            f.write(sec["content_html"])
            f.write("\n\n" + "=" * 50 + "\n\n")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract <h1> and <h2> sections and their content from HTML.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input HTML file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output text file.")
    args = parser.parse_args()

    # Run the main function
    main(args.input, args.output)
