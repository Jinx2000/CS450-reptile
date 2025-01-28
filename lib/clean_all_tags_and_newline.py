#!/usr/bin/env python3

import re
import argparse
from bs4 import BeautifulSoup

CHUNK_PATTERN = re.compile(
    r"(===== CONCEPT CHUNK #\d+ =====.*?========================================)",
    re.DOTALL
)

def preserve_code_blocks_and_clean_text(text: str) -> str:
    """
    Processes the text, preserving the content within code blocks as-is, 
    while cleaning and formatting the text outside the code blocks.
    """
    code_block_pattern = r"\[CODE_BLOCK_START\](.*?)\[CODE_BLOCK_END\]"
    cleaned_parts = []
    last_end = 0

    # Iterate through all code block matches
    for match in re.finditer(code_block_pattern, text, flags=re.DOTALL):
        start, end = match.span()
        code_block_content = match.group(0)  # Preserve the entire block as-is

        # Process the text outside the code block
        outside_text = text[last_end:start]
        cleaned_parts.append(clean_text_outside_code(outside_text))

        # Add the preserved code block without modification
        cleaned_parts.append(code_block_content)
        last_end = end

    # Process any remaining text after the last code block
    remaining_text = text[last_end:]
    cleaned_parts.append(clean_text_outside_code(remaining_text))

    # Join all parts together
    return "".join(cleaned_parts)

def clean_text_outside_code(text: str) -> str:
    """
    Cleans and formats the text outside of code blocks:
    - Removes HTML tags
    - Normalizes whitespace
    - Splits sentences to ensure each ends on a new line
    """
    # 1. Remove remaining HTML tags using BeautifulSoup
    soup = BeautifulSoup(text, "html.parser")
    clean_text = soup.get_text(separator=" ")  # Separate tags with single spaces

    # 2. Collapse multiple whitespaces into a single space
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    # 3. Split sentences at periods
    clean_text = re.sub(r"\.(?=\s|$)", ".\n", clean_text)

    # 4. Remove extra blank lines
    lines = [line.strip() for line in clean_text.splitlines()]
    return "\n".join(line for line in lines if line)

def process_concept_chunk(full_chunk: str) -> str:
    """
    Processes a CONCEPT CHUNK, preserving code blocks as-is and cleaning the rest of the content.
    """
    # Extract the content after "Content:"
    content_marker = "Content:"
    content_start = full_chunk.find(content_marker)
    if content_start == -1:
        return full_chunk  # No content found, return as-is

    content_to_clean = full_chunk[content_start + len(content_marker):].strip()

    # Preserve code blocks and clean text outside them
    cleaned_content = preserve_code_blocks_and_clean_text(content_to_clean)

    # Add newlines around [CODE_BLOCK_START] and [CODE_BLOCK_END]
    cleaned_content = re.sub(r"\[CODE_BLOCK_START\]", r"\n[CODE_BLOCK_START]", cleaned_content)
    cleaned_content = re.sub(r"\[CODE_BLOCK_END\]", r"[CODE_BLOCK_END]\n", cleaned_content)

    # Reassemble the chunk with cleaned content
    header = full_chunk[:content_start + len(content_marker)].strip()
    return f"{header}\n\n{cleaned_content}\n"

def process_file(input_file: str, output_file: str) -> None:
    """
    Reads the file, processes each CONCEPT CHUNK, and writes the output to a file.
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
        processed_chunk = process_concept_chunk(chunk_text)
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
