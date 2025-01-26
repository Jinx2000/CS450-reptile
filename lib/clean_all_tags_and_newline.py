#!/usr/bin/env python3

import re
import argparse
from bs4 import BeautifulSoup

CHUNK_PATTERN = re.compile(
    r"(===== CATEGORY CHUNK #\d+ =====.*?========================================)",
    re.DOTALL
)

def remove_html_and_split_sentences(text: str) -> str:
    """
    Removes all HTML tags, normalizes whitespace, and ensures each sentence
    ends on a new line. Also treats '========[code block X]========' as its own sentence.
    """
    # 1. Remove HTML tags using BeautifulSoup
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(separator=" ")  # separate tags with single spaces

    # 2. Collapse multiple whitespace into a single space
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    # 3. Split sentences ending with a period or special code block pattern
    clean_text = re.sub(r"\.(?=\s|$)", ".\n", clean_text)
    clean_text = re.sub(r"(========\[code block.*?\]========)", r"\n\1\n", clean_text)

    # 4. Clean up any extra blank lines or leading/trailing spaces
    lines = [line.strip() for line in clean_text.splitlines()]
    final_text = "\n".join(line for line in lines if line)

    return final_text

def process_modified_chunk(full_chunk: str) -> str:
    """
    Processes the '=== Modified Chunk ===' part of a category chunk, removing HTML
    and splitting sentences while leaving the rest unchanged.
    """
    # Find the start of the Modified Chunk section
    modified_chunk_start = full_chunk.find("=== Modified Chunk ===")
    if modified_chunk_start == -1:
        return full_chunk  # If no Modified Chunk, return as-is

    kept_marker_index = full_chunk.find("=== Kept", modified_chunk_start)
    end_of_chunk_index = full_chunk.find("========================================", modified_chunk_start)

    if kept_marker_index == -1:
        kept_marker_index = end_of_chunk_index
    if kept_marker_index == -1:
        return full_chunk

    # Split the chunk into parts
    before_modified = full_chunk[:modified_chunk_start]
    modified_part = full_chunk[modified_chunk_start:kept_marker_index]
    after_modified = full_chunk[kept_marker_index:]

    # Extract the heading and content of the Modified Chunk
    heading_line = "=== Modified Chunk ==="
    content_start = modified_part.find(heading_line) + len(heading_line)
    heading_prefix = modified_part[:content_start]
    content_to_clean = modified_part[content_start:]

    # Clean the content and reassemble the chunk
    cleaned_content = remove_html_and_split_sentences(content_to_clean)
    processed_modified_part = heading_prefix + cleaned_content

    return before_modified + processed_modified_part + after_modified

def process_file(input_file: str, output_file: str) -> None:
    """
    Reads the file, processes each CATEGORY CHUNK, and writes the output to a file.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        all_text = infile.read()

    chunks = CHUNK_PATTERN.findall(all_text)
    processed_output = []
    last_pos = 0

    for match in CHUNK_PATTERN.finditer(all_text):
        outside_text = all_text[last_pos:match.start()]
        if outside_text:
            processed_output.append(outside_text)

        chunk_text = match.group(1)
        processed_chunk = process_modified_chunk(chunk_text)
        processed_output.append(processed_chunk)
        last_pos = match.end()

    if last_pos < len(all_text):
        processed_output.append(all_text[last_pos:])

    final_text = "".join(processed_output)

    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write(final_text)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean HTML tags and normalize sentences in a text file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file.")
    args = parser.parse_args()

    process_file(args.input, args.output)
