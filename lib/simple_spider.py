import requests
from bs4 import BeautifulSoup
import argparse

def extract_td_content(url: str, output_file: str) -> None:
    """
    Fetches the HTML from 'url', parses it, and extracts all <div class="td-content"> sections.
    Writes the extracted HTML to 'output_file'.
    """
    try:
        # 1. Retrieve the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx or 5xx

        # 2. Parse the HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # 3. Find all <div class="td-content">
        td_content_divs = soup.find_all("div", class_="td-content")

        # 4. Extract the inner HTML or text from those divs
        extracted_content_list = []
        for div in td_content_divs:
            extracted_html = str(div)  # Keep the HTML content
            extracted_content_list.append(extracted_html)

        # Combine everything (in case there are multiple .td-content divs)
        final_output = "\n\n".join(extracted_content_list)

        # 5. Write the result to a file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"Extracted <div class='td-content'> sections saved to {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract <div class='td-content'> sections from a webpage.")
    parser.add_argument("--url", type=str, required=True, help="The URL of the webpage to scrape.")
    parser.add_argument("--output", type=str, required=True, help="The output file to save the extracted content.")

    args = parser.parse_args()

    # Run the extraction
    extract_td_content(args.url, args.output)
