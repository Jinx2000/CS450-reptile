# Kubernetes Documentation Processing Workflow

A streamlined pipeline to scrape, clean, annotate links, and convert Kubernetes documentation (or related content) into a structured CSV file. This workflow makes it easy to reuse extracted information for knowledge bases or other documentation tools.

---

## Table of Contents
1. [Overview](#1-overview)
2. [Key Features](#2-key-features)
3. [Project Structure](#3-project-structure)
4. [Workflow](#4-workflow)
5. [Usage](#5-usage)
   - [Single URL](#single-url)
   - [Multiple URLs](#multiple-urls)
6. [Dependencies](#6-dependencies)
7. [Troubleshooting](#7-troubleshooting)


---

## 1. Overview

This project automates the process of extracting, annotating, and transforming content from Kubernetes-related documentation into a structured CSV file. Specifically, it:
- Scrapes the content from a user-provided URL.
- Annotates all `<a>` tags by converting them to a custom inline format (e.g., Some Text [LINK:https://example.com]).
- Organizes the extracted data into logical sections and code blocks.
- Removes unnecessary HTML tags and ensures readability.
- Outputs a CSV file with fields such as title, content, usage examples, category, tags, references, and extracted links.

These steps produce a clean, organized dataset suitable for further analysis or integration with other platforms.

---

## 2. Key Features

1. Inline Link Annotations
   - `<a>` tags are replaced with [LINK:href] notations, preserving anchor text while making link parsing simpler in subsequent steps.

2. CSV “link to” Column
   - A post-processing script (add_link_to.py) extracts any [LINK:...] annotations from the content and places them in a dedicated “link to” CSV column (with support for relative-link resolution via a base URL).

3. Dynamic Category Assignment
   - The category column in the final CSV is derived from the last word in the URL (e.g., Ingress, Gateway).

4. Reference URL
   - Each CSV entry includes the original source URL for easy traceability.

5. Intermediate Outputs
   - Each step writes intermediate files to data/ so you can inspect or debug the pipeline.

6. Multiple URL Support
   - Use Multi_facade.py to run the entire workflow against multiple URLs at once, combining all results into a single CSV.

---

## 3. Project Structure

Below is a simplified layout of the repository:

Facade.py
Multi_facade.py
lib/
  simple_spider.py
  clean_html_links.py
  extract_h2.py
  extract_code_example.py
  clean_all_tags_and_newline.py
  final_refine.py
  to_csv.py
  add_link_to.py
data/
  multi_url.txt (optional list of URLs)
  ...
  final_output_`<category>`.csv (generated by Facade.py)
  multi_final.csv (generated by Multi_facade.py)
requirements.txt
README.md

- Facade.py: Main script orchestrating all the steps for one URL.
- Multi_facade.py: Higher-level script that runs Facade for multiple URLs and merges the outputs.
- lib/: Individual Python scripts for each step in the data processing pipeline.
- data/: Contains intermediate files, final CSV outputs, and an optional list of URLs (multi_url.txt).

---

## 4. Workflow

The workflow is executed in sequential steps. When you run Facade.py, it will:

1. simple_spider.py
   - Input: --url command-line argument.
   - Action: Scrapes HTML from the given URL, extracting `<div class="td-content">` sections.
   - Output: data/step1_spider_output.txt

2. clean_html_links.py
   - Action: Replaces every `<a>` tag with inner_text [LINK:href].
   - Output: data/step2_clean_links_output.txt

3. extract_h2.py
   - Action: Segments the HTML into logical chunks based on `<h2>` headings.
   - Output: data/step3_extract_h2_output.txt

4. extract_code_example.py
   - Action: Identifies and processes `<code>` blocks, optionally removing or retaining them based on your logic.
   - Output: data/step4_extract_code_output.txt

5. clean_all_tags_and_newline.py
   - Action: Strips out any remaining HTML tags and ensures each sentence ends with a newline for readability.
   - Output: data/step5_clean_tags_output.txt

6. final_refine.py
   - Action: Applies any final text clean-ups (e.g., removing extra spaces or handling edge cases).
   - Output: data/step6_final_refine_output.txt

7. to_csv.py
   - Action: Converts the processed text into a CSV, adding category (derived from the URL) and reference (the original URL).
   - Output: data/output_initial.csv

8. add_link_to.py
   - Action: Parses the content column in the CSV for [LINK:...] annotations, removes them from the content, and places them into a new “link to” column. It also makes links clickable by prepending a base URL if needed.
   - Output: Final CSV file named data/final_output_`<category>`.csv

---

## 5. Usage

### A. Single URL

Run the workflow end-to-end for a single URL with Facade.py:
```bash
python3 Facade.py 
```
Arguments:
- --url: The URL to scrape. Defaults to https://kubernetes.io/docs/concepts/services-networking/ingress/ if not provided.

Outputs:
- Intermediate files in data/...
- A final CSV: data/final_output_Kubernetes_ingress.csv (or equivalent category based on the URL).

### B. Multiple URLs

For processing multiple URLs, use Multi_facade.py:

1. Create (or edit) a text file with one URL per line, e.g., data/multi_url.txt.
2. Run:
```bash
python3 Multi_facade.py 
```
- --input: Points to the file containing multiple URLs (defaults to data/multi_url.txt).
- --output: The combined CSV with data from all URLs (defaults to data/multi_final.csv).

Process:
1. For each URL, Multi_facade.py calls Facade.py internally.
2. It moves each final CSV (e.g., final_output_Kubernetes_ingress.csv, etc.) to a temporary folder data/multi_temp_csv/.
3. Once all URLs are processed, it combines them into a single CSV file `multi_final.csv`.

---

## 6. Dependencies

- requests – Fetches HTML from the web.
- beautifulsoup4 – Parses HTML content.
- re (built-in) – Regex processing for link annotations and text cleaning.
- csv (built-in) – Reading and writing CSV files.
- argparse (built-in) – Handling command-line arguments.
- shutil (built-in) – Used in Multi_facade.py for folder operations.

Installation:
```bash
pip install -r requirements.txt
```
---

## 7. Troubleshooting

1. Missing data/ Folder
   - The scripts create data/ automatically if it does not exist, but ensure you have write permissions.

2. Empty or Corrupted Intermediate Files
   - Check the console output for errors in earlier steps.
   - Verify the URL actually contains `<div class="td-content">` elements for scraping.

3. Links Are Not Populating
   - Confirm that `<a>` tags existed in the scraped content.
   - Make sure the base URL is correct in Facade.py if you need to convert relative links.

4. Multiple URLs Failing
   - Confirm each URL in multi_url.txt is valid.
   - Check if network or SSL errors occur for certain sites.

---

