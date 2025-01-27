import os
import subprocess
import argparse

def ensure_data_folder():
    """Ensure the 'data' folder exists in the current directory."""
    if not os.path.exists("data"):
        os.makedirs("data")

def extract_category_from_url(url: str) -> str:
    """
    Extracts the last word of the URL (e.g., 'ingress' or 'gateway') to form the category.
    """
    last_word = url.rstrip("/").split("/")[-1]
    return f"Kubernetes_{last_word}"

def run_workflow(website_url):
    """Runs the entire workflow and stores intermediate files in the 'data' folder."""
    ensure_data_folder()

    # Define intermediate file paths
    spider_output = "data/step1_spider_output.txt"
    clean_links_output = "data/step2_clean_links_output.txt"
    extract_h2_output = "data/step3_extract_h2_output.txt"
    extract_code_output = "data/step4_extract_code_output.txt"
    clean_tags_output = "data/step5_clean_tags_output.txt"
    refined_output = "data/step6_final_refine_output.txt"
    initial_csv = "data/output_initial.csv"

    # Extract the category from the URL
    category = extract_category_from_url(website_url)

    try:
        # Step 1: Run the simple_spider.py script
        subprocess.run(["python3", "lib/simple_spider.py", "--url", website_url, "--output", spider_output], check=True)

        # Step 2: Run the clean_html_links.py script
        subprocess.run(["python3", "lib/clean_html_links.py", "--input", spider_output, "--output", clean_links_output], check=True)

        # Step 3: Run the extract_h2.py script
        subprocess.run(["python3", "lib/extract_h2.py", "--input", clean_links_output, "--output", extract_h2_output], check=True)

        # Step 4: Run the extract_code_example.py script
        subprocess.run(["python3", "lib/extract_code_example.py", "--input", extract_h2_output, "--output", extract_code_output], check=True)

        # Step 5: Run the clean_all_tags_and_newline.py script
        subprocess.run(["python3", "lib/clean_all_tags_and_newline.py", "--input", extract_code_output, "--output", clean_tags_output], check=True)

        # Step 6: Run the final_refine.py script
        subprocess.run(["python3", "lib/final_refine.py", "--input", clean_tags_output, "--output", refined_output], check=True)

        # Step 7: Generate initial CSV with to_csv.py
        subprocess.run([
            "python3", "lib/to_csv.py", 
            "--input", refined_output, 
            "--output", initial_csv, 
            "--category", category, 
            "--reference", website_url
        ], check=True)

        # Step 8: Add links to the final CSV
        final_csv = f"data/final_output_{category}.csv"
        subprocess.run([
            "python3", "lib/add_link_to.py", 
            "--input", initial_csv, 
            "--output", final_csv
        ], check=True)

        print(f"Workflow complete! Final output saved to {final_csv}")
    except subprocess.CalledProcessError as e:
        print(f"Error during workflow execution: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full workflow for web scraping and processing.")
    parser.add_argument(
        "--url",
        type=str,
        default="https://kubernetes.io/docs/concepts/services-networking/ingress/",
        help="The website URL to scrape (default: Kubernetes Ingress documentation)."
    )
    args = parser.parse_args()

    run_workflow(args.url)
