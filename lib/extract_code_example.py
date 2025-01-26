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

def extract_code_from_html(html: str):
    """Extract code blocks from HTML using BeautifulSoup."""
    soup = BeautifulSoup(html, "html.parser")
    code_elements = soup.find_all("code")
    code_texts = [c.get_text() for c in code_elements]
    return code_texts, soup

def should_keep_code_block(code_block: str) -> bool:
    """Determine whether a code block should be kept."""
    lines = code_block.strip().splitlines()
    special_keywords = ["--watch-ingress-without-class", "kubectl"]
    return any(kw in code_block for kw in special_keywords) or len(lines) >= 3

def replace_code_in_soup(soup: BeautifulSoup, keep_map: dict) -> None:
    """Replace code blocks in the soup with placeholders."""
    all_code_elements = soup.find_all("code")
    used_containers = set()
    for code_elt in all_code_elements:
        container = code_elt
        for parent in code_elt.parents:
            if parent.name in ["div", "pre"]:
                class_list = parent.get("class") or []
                if any(cls in ["highlight", "code-sample", "includecode"] for cls in class_list):
                    container = parent
                    break
        if container not in used_containers:
            used_containers.add(container)
            idx = keep_map.get(code_elt)
            placeholder = f"========[code block {idx}]========" if idx else code_elt.get_text(strip=True)
            container.replace_with(placeholder)

def main(input_file: str, output_file: str):
    """Main function to process input and output files."""
    with open(input_file, "r", encoding="utf-8") as f:
        full_text = f.read()

    chunks = split_into_chunks(full_text)
    results = []

    for i, chunk in enumerate(chunks, start=1):
        html_part = get_html_portion(chunk)
        if not html_part:
            results.append({
                "modified_chunk": chunk,
                "kept_code_blocks": []
            })
            continue

        code_texts, soup = extract_code_from_html(html_part)
        keep_flags = [should_keep_code_block(ct) for ct in code_texts]

        kept_code_blocks = []
        keep_map = {}
        code_block_counter = 0

        for idx, code_str in enumerate(code_texts, start=1):
            if keep_flags[idx - 1]:
                code_block_counter += 1
                kept_code_blocks.append(code_str)
                code_elt = soup.find_all("code")[idx - 1]
                keep_map[code_elt] = code_block_counter

        replace_code_in_soup(soup, keep_map)
        modified_html = str(soup)

        marker = "Content:"
        idx = chunk.find(marker)
        if idx != -1:
            prefix = chunk[:idx + len(marker)].rstrip()
            modified_chunk = prefix + "\n" + modified_html.strip()
        else:
            modified_chunk = chunk

        results.append({
            "modified_chunk": modified_chunk,
            "kept_code_blocks": kept_code_blocks
        })

    with open(output_file, "w", encoding="utf-8") as out:
        for i, entry in enumerate(results, start=1):
            out.write(f"===== CATEGORY CHUNK #{i} =====\n\n")
            out.write("=== Modified Chunk ===\n")
            out.write(entry["modified_chunk"])
            out.write("\n\n")
            if entry["kept_code_blocks"]:
                out.write(f"=== Kept {len(entry['kept_code_blocks'])} Code Block(s) ===\n")
                for j, code_text in enumerate(entry["kept_code_blocks"], start=1):
                    out.write(f"[Code Block {j}]:\n")
                    out.write(code_text.strip())
                    out.write("\n\n")
            else:
                out.write("=== No code blocks kept ===\n\n")
            out.write("========================================\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract and refine code examples from chunks.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file.")
    args = parser.parse_args()

    main(args.input, args.output)
