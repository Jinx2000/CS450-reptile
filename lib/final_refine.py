import re
import argparse

def process_text(text: str) -> str:
    """
    1. If "=== No code blocks kept ===========================================" 
       is found, turn it into:
          \n=== No code blocks kept ===\n========================================
    2. Surround lines containing '=== Kept N Code Block(s) ===' with a 
       blank line before and after.
    3. Add a newline before any '[N] Category Title: something Content:' sequence,
       and also a newline just before 'Content:' on that same line.
    """
    # 0) Handle "No code blocks kept" special case:
    text = text.replace(
        "=== No code blocks kept ===========================================",
        "\n=== No code blocks kept ===\n========================================"
    )

    # 1) Surround "=== Kept N Code Block(s) ===" with blank lines.
    pattern_kept = r"(=== Kept \d+ Code Block\(s\) ===)"
    text = re.sub(pattern_kept, r"\n\1\n", text)

    # 2) Insert a newline before "[N] Category Title:" if it is immediately preceded by other text.
    text = re.sub(r"([^\n])(\[\d+\]\s*Category Title:)", r"\1\n\2", text)

    # 3) Insert a newline before the literal "Content:" on that same line.
    text = re.sub(r"(\[\d+\]\s*Category Title:.*?)(Content:)", r"\1\n\2", text, flags=re.DOTALL)

    return text

def main(input_file: str, output_file: str) -> None:
    """
    Reads 'input_file', applies the above text transformations,
    then writes the result to 'output_file'.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        original_text = f.read()

    # Process the text with our rules
    transformed_text = process_text(original_text)

    # Write to output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transformed_text)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Apply final text refinements to a processed file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file.")
    args = parser.parse_args()

    # Run the main function
    main(args.input, args.output)
