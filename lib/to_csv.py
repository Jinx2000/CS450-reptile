import re
import csv
import argparse

DEFAULT_CATEGORY = "Kubernetes Ingress"

CHUNK_PATTERN = re.compile(
    r"(===== CATEGORY CHUNK #\d+ =====.*?========================================)",
    re.DOTALL
)

def remove_separators(text: str) -> str:
    """
    Remove lines containing '===' or '========================================' from the text.
    """
    lines = text.splitlines()
    filtered_lines = [line for line in lines if "===" not in line and "========================================" not in line]
    return "\n".join(filtered_lines)

def parse_chunk(chunk_text: str):
    """
    Parse CATEGORY CHUNK text to extract title, content, usage examples, etc.
    Returns a list of dictionaries.
    """
    title_match = re.search(r"\[\d+\]\s*Category Title:\s*(.*?)(?=\n|Content:)", chunk_text)
    title_str = title_match.group(1).strip() if title_match else "Unknown Title"

    modified_chunk_match = re.search(
        r"(=== Modified Chunk ===.*?)(?==== Kept|=== No code blocks kept|========================================|$)",
        chunk_text,
        re.DOTALL
    )
    if not modified_chunk_match:
        return []

    modified_text = modified_chunk_match.group(1)

    content_pos = modified_text.find("Content:")
    if content_pos != -1:
        modified_text = modified_text[content_pos + len("Content:"):].strip()
    else:
        modified_text = re.sub(r"=== Modified Chunk ===", "", modified_text).strip()

    no_code_kept_match = re.search(r"=== No code blocks kept ===", chunk_text)
    if no_code_kept_match:
        content_cleaned = remove_separators(modified_text)
        return [{
            "title": title_str,
            "content": content_cleaned,
            "usage_example": "None",
            "category": DEFAULT_CATEGORY,
            "tags": "None",
            "reference": "None"
        }]

    kept_section_match = re.search(r"(=== Kept\s*\d+\s*Code Block\(s\) ===.*)", chunk_text, re.DOTALL)
    if not kept_section_match:
        content_cleaned = remove_separators(modified_text)
        return [{
            "title": title_str,
            "content": content_cleaned,
            "usage_example": "None",
            "category": DEFAULT_CATEGORY,
            "tags": "None",
            "reference": "None"
        }]

    kept_section = kept_section_match.group(1)

    placeholder_re = re.compile(r"========\[code block\s*(\d+)\]========")
    split_parts = placeholder_re.split(modified_text)
    content_for_block = {}
    current_block_index = None

    for i, part in enumerate(split_parts):
        if i % 2 == 0:
            if current_block_index is not None:
                content_for_block[current_block_index] += "\n" + part.strip()
        else:
            current_block_index = int(part.strip())
            content_for_block[current_block_index] = ""

    placeholders_found = placeholder_re.findall(modified_text)
    if placeholders_found and split_parts[0].strip():
        first_block_idx = int(placeholders_found[0])
        content_for_block[first_block_idx] = split_parts[0].strip() + "\n" + content_for_block[first_block_idx]

    block_usage_pattern = re.compile(
        r"\[Code Block\s+(\d+)\]:\s*(.*?)(?=\n\[Code Block\s+\d+\]:|$)",
        re.DOTALL
    )
    usage_for_block = {
        int(num): content.strip()
        for num, content in block_usage_pattern.findall(kept_section)
    }

    documents = []
    used_block_indices = sorted(usage_for_block.keys())
    for b_idx in used_block_indices:
        raw_content = content_for_block.get(b_idx, "").strip()
        raw_usage = usage_for_block[b_idx]

        cleaned_content = remove_separators(raw_content)
        cleaned_usage = remove_separators(raw_usage)

        documents.append({
            "title": title_str,
            "content": cleaned_content,
            "usage_example": cleaned_usage,
            "category": DEFAULT_CATEGORY,
            "tags": "None",
            "reference": "None"
        })

    if not documents:
        cleaned_content = remove_separators(modified_text)
        return [{
            "title": title_str,
            "content": cleaned_content,
            "usage_example": "None",
            "category": DEFAULT_CATEGORY,
            "tags": "None",
            "reference": "None"
        }]

    return documents

def process_file_to_csv(input_file: str, output_file: str):
    """
    Reads a text file containing CATEGORY CHUNK sections and writes them to a CSV file.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        all_text = infile.read()

    chunks = CHUNK_PATTERN.findall(all_text)
    all_documents = [doc for chunk in chunks for doc in parse_chunk(chunk)]

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        writer.writerow(["document_id", "title", "content", "usage_example", "category", "tags", "reference"])

        for doc_id, doc in enumerate(all_documents, start=1):
            writer.writerow([
                doc_id,
                doc["title"],
                doc["content"],
                doc["usage_example"],
                doc["category"],
                doc["tags"],
                doc["reference"]
            ])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert processed CATEGORY CHUNK text to a CSV format.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input text file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output CSV file.")
    args = parser.parse_args()

    process_file_to_csv(args.input, args.output)
