import os
import subprocess
import argparse
import shutil
import csv

def ensure_data_folder():
    """Ensure the 'data/multi_temp_csv' folder exists and clear it at the start of a new run."""
    temp_folder = "data/multi_temp_csv"
    if os.path.exists(temp_folder):
        # Clear the folder at the beginning of the run
        shutil.rmtree(temp_folder)
    os.makedirs(temp_folder)

def create_default_url_file(input_file: str):
    """Create a default multi_url.txt file if it doesn't exist."""
    default_urls = [
        "https://kubernetes.io/docs/concepts/services-networking/ingress/",
        "https://kubernetes.io/docs/concepts/services-networking/gateway/"
    ]
    if not os.path.exists(input_file):
        os.makedirs(os.path.dirname(input_file), exist_ok=True)
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("\n".join(default_urls))
        print(f"Default URL file created at {input_file}")

def extract_topic_from_url(url: str) -> str:
    """Extracts the last word of the URL (e.g., 'ingress' or 'gateway') to form the topic."""
    last_word = url.rstrip("/").split("/")[-1]
    return last_word.capitalize()

def run_facade_for_url(website_url: str):
    """Run the Facade.py workflow for a single URL."""
    # Run Facade.py for the given URL
    subprocess.run([
        "python3", "Facade.py",
        "--url", website_url
    ], check=True)

    # Identify the expected output file
    topic = extract_topic_from_url(website_url)
    generated_csv = f"data/final_output_{topic}.csv"

    if not os.path.exists(generated_csv):
        raise FileNotFoundError(f"Expected output CSV not found: {generated_csv}")

    # Move the generated CSV to the temp folder
    temp_csv = f"data/multi_temp_csv/final_output_{topic}.csv"
    os.rename(generated_csv, temp_csv)
    return temp_csv

def combine_csvs(output_csvs: list, final_csv: str):
    """Combine all individual CSVs into one final CSV."""
    header_written = False

    with open(final_csv, "w", newline="", encoding="utf-8") as outfile:
        writer = None

        for csv_file in output_csvs:
            with open(csv_file, "r", encoding="utf-8") as infile:
                reader = csv.reader(infile)
                headers = next(reader)

                # Write headers only once
                if not header_written:
                    writer = csv.writer(outfile)
                    writer.writerow(headers)
                    header_written = True

                # Write the rows
                for row in reader:
                    writer.writerow(row)

    print(f"Combined CSV saved to {final_csv}")

def run_multi_facade(input_file: str, final_csv: str):
    """Run the Facade workflow for multiple URLs and combine the results."""
    ensure_data_folder()
    create_default_url_file(input_file)

    # Read the list of URLs from the input file
    with open(input_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    # Temporary storage for output CSVs from each URL
    output_csvs = []

    for url in urls:
        try:
            print(f"Processing URL: {url}")
            temp_csv = run_facade_for_url(url)
            output_csvs.append(temp_csv)
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing URL {url}: {e}")

    # Combine all CSVs into one final CSV
    combine_csvs(output_csvs, final_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Facade.py for multiple URLs and combine results.")
    parser.add_argument("--input", type=str, default="data/multi_url.txt", help="Path to the file containing multiple URLs.")
    parser.add_argument("--output", type=str, default="data/multi_final.csv", help="Path to the combined output CSV.")
    args = parser.parse_args()

    run_multi_facade(args.input, args.output)
