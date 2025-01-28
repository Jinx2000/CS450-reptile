#!/usr/bin/env python3

import argparse

def process_text(text: str) -> str:
    """
    Removes all exact matches of "==========" from the input text.
    """
    return text.replace("==========", "").strip()

def main(input_file: str, output_file: str) -> None:
    """
    Reads 'input_file', applies the above text transformations,
    then writes the result to 'output_file'.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        original_text = f.read()

    # Process the text to remove "=========="
    transformed_text = process_text(original_text)

    # Write the cleaned result to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transformed_text)

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Remove exact matches of '==========' from a text file.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file.")
    args = parser.parse_args()

    # Run the main function
    main(args.input, args.output)
