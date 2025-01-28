#!/usr/bin/env python3

import argparse
from bs4 import BeautifulSoup

SEPARATOR = "=================================================="

def split_into_chunks(full_text: str):
    """Split the text into chunks by SEPARATOR."""
    chunks = full_text.split(SEPARATOR)
    return [ch.strip() for ch in chunks if ch.strip()]

def get_html_portion(chunk: str):
    """Extract the HTML portion after 'Content:' in the chunk."""
    marker = "Content:"
    idx = chunk.find(marker)
    return chunk[idx + len(marker):].lstrip() if idx != -1 else ""

def should_treat_as_code_block(code_text: str) -> bool:
    """
    Determine whether a code block should be treated as a full code block.
    - Return False if the code block is simple (e.g., one or two words without punctuation).
    - Return True if it contains punctuation (like '.') or has more than two words.
    """
    # Split the code block into words
    words = code_text.split()
    # Check if it contains punctuation or is complex
    if "." in code_text or len(words) > 2:
        return True
    return False

def embed_code_blocks(html: str):
    """
    Parse the HTML using BeautifulSoup and embed code blocks in the content.
    - Simple code blocks (e.g., single words) are added as plain text.
    - Complex code blocks are wrapped with [CODE_BLOCK_START] and [CODE_BLOCK_END].
    """
    soup = BeautifulSoup(html, "html.parser")
    all_code_elements = soup.find_all("code")

    for code_elt in all_code_elements:
        # Extract the code text
        code_text = code_elt.get_text().strip()

        if should_treat_as_code_block(code_text):
            # Treat as a full code block
            wrapped_code = f"\n[CODE_BLOCK_START]\n{code_text}\n[CODE_BLOCK_END]\n"
            code_elt.replace_with(wrapped_code)
        else:
            # Treat as simple text
            code_elt.replace_with(code_text)

    # Return the modified HTML as a string
    return str(soup)

def main(input_file: str, output_file: str):
    """
    Main function to process input and output files.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    # Separate the TOPIC line from the rest of the text
    lines = full_text.splitlines()
    topic_line = lines[0] if lines[0].startswith("[TOPIC:") else "Unknown Topic"
    rest_of_text = "\n".join(lines[1:])

    chunks = split_into_chunks(rest_of_text)
    results = []

    for i, chunk in enumerate(chunks, start=1):
        html_part = get_html_portion(chunk)
        if not html_part:
            # If there's no HTML part, keep the chunk as-is
            results.append(chunk)
            continue

        # Embed code blocks in the HTML content
        modified_html = embed_code_blocks(html_part)

        # Combine the prefix and modified HTML
        marker = "Content:"
        idx = chunk.find(marker)
        if idx != -1:
            prefix = chunk[:idx + len(marker)].rstrip()
            modified_chunk = prefix + "\n" + modified_html.strip()
        else:
            modified_chunk = chunk

        # Append the processed chunk
        results.append(modified_chunk)

    # Write the processed chunks to the output file
    with open(output_file, "w", encoding="utf-8") as out:
        # Write the TOPIC at the top of the file
        out.write(f"{topic_line}\n\n")
        for i, modified_chunk in enumerate(results, start=1):
            out.write(f"===== CONCEPT CHUNK #{i} =====\n\n")
            out.write(modified_chunk)
            out.write("\n\n" + SEPARATOR + "\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed code blocks in content and refine output.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file.")
    args = parser.parse_args()

    main(args.input, args.output)
