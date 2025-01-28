import re
import csv
import argparse

CHUNK_PATTERN = re.compile(
    r"(===== CONCEPT CHUNK #\d+ =====.*?========================================)",
    re.DOTALL
)

def extract_topic(full_text: str) -> str:
    """
    Extract the topic from the text's first line in the format [TOPIC: ...].
    """
    topic_match = re.search(r"\[TOPIC:\s*(.*?)\]", full_text)
    return topic_match.group(1).strip() if topic_match else "Unknown Topic"

def parse_chunk(chunk_text: str, category: str, reference: str, root_url: str):
    """
    Parse CONCEPT CHUNK text to extract Concept, Content, and Links.
    """
    # Extract Concept and ID
    concept_match = re.search(r"\[\d+\]\s*Concept:\s*(.*?)\s*\[id:\s*(.*?)\]", chunk_text, re.DOTALL)
    concept_str = concept_match.group(1).strip() if concept_match else "Unknown Concept"
    concept_id = concept_match.group(2).strip() if concept_match and concept_match.group(2) else None

    # Extract Content
    content_match = re.search(r"Content:\s*(.*)", chunk_text, re.DOTALL)
    content_str = content_match.group(1).strip() if content_match else "Unknown Content"

    # Construct full URL for the concept
    concept_url = f"{reference}#{concept_id}" if concept_id else reference

    # Extract links and make them clickable
    link_pattern = r"\[LINK:(.*?)\]"
    links = re.findall(link_pattern, content_str)
    clickable_links = []
    for link in links:
        if link.startswith("#"):  # Fragment link
            clickable_links.append(f"{reference}{link}")
        elif link.startswith("/"):  # Relative link
            clickable_links.append(f"{root_url}{link}")
        else:
            clickable_links.append(link)  # Unhandled cases (kept as is)

    # Remove [LINK:...] annotations from the content
    cleaned_content = re.sub(link_pattern, "", content_str).strip()

    # Return parsed data
    return {
        "Concept": concept_str,
        "Content": cleaned_content,
        "URL": concept_url,
        "Link to": "\n".join(clickable_links),
        "Tags": "None",
        "Category": category
    }

def process_file_to_csv(input_file: str, output_file: str, category: str, reference: str, root_url: str):
    """
    Reads a text file containing CONCEPT CHUNK sections, extracts rows, 
    and writes them to a CSV file.
    """
    with open(input_file, "r", encoding="utf-8") as infile:
        all_text = infile.read()

    # Extract the topic from the file
    topic = extract_topic(all_text)

    # Extract all chunks
    chunks = CHUNK_PATTERN.findall(all_text)

    # Parse each chunk into a row
    all_rows = [parse_chunk(chunk, category, reference, root_url) for chunk in chunks]

    # Write the CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=["ID", "Category", "Topic", "Concept", "Content", "URL", "Link to", "Tags"]
        )
        writer.writeheader()

        # Write rows with a unique ID for each document
        for idx, row in enumerate(all_rows, start=1):
            writer.writerow({
                "ID": idx,
                "Category": row["Category"],
                "Topic": topic,
                "Concept": row["Concept"],
                "Content": row["Content"],
                "URL": row["URL"],
                "Link to": row["Link to"],
                "Tags": row["Tags"]
            })

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert processed CONCEPT CHUNK text to a CSV format.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input text file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output CSV file.")
    parser.add_argument("--category", type=str, required=True, help="Category name to assign to each document.")
    parser.add_argument("--reference", type=str, required=True, help="Base URL to construct concept-specific links.")
    parser.add_argument("--root-url", type=str, required=True, help="Root URL to prepend to relative links.")
    args = parser.parse_args()

    process_file_to_csv(args.input, args.output, args.category, args.reference, args.root_url)
