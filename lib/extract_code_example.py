#!/usr/bin/env python3

import argparse
import re
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

def embed_code_blocks(html: str):
    """
    Parse the HTML using BeautifulSoup and embed code blocks in the content.
    The code blocks are wrapped with [CODE_BLOCK_START] and [CODE_BLOCK_END].
    """
    soup = BeautifulSoup(html, "html.parser")
    all_code_elements = soup.find_all("code")

    for code_elt in all_code_elements:
        # Extract the code text
        code_text = code_elt.get_text()
        # Replace the code element with wrapped plain text
        wrapped_code = f"\n[CODE_BLOCK_START]\n{code_text.strip()}\n[CODE_BLOCK_END]\n"
        code_elt.replace_with(wrapped_code)

    # Return the modified HTML as a string
    return str(soup)

def main(input_file: str, output_file: str):
    """
    Main function to process input and output files.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    chunks = split_into_chunks(full_text)
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
        for i, modified_chunk in enumerate(results, start=1):
            out.write(f"===== CATEGORY CHUNK #{i} =====\n\n")
            out.write("=== Modified Chunk ===\n")
            out.write(modified_chunk)
            out.write("\n\n" + SEPARATOR + "\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed code blocks in content and refine output.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file.")
    args = parser.parse_args()

    main(args.input, args.output)
