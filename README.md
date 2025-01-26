# Kubernetes Documentation Processing Workflow

---

## Purpose

This project automates the process of extracting, cleaning, and transforming documentation from a Kubernetes-related website into a structured CSV file. The primary goal is to:
- Scrape and parse the relevant documentation from the web.
- Clean up the extracted content by removing unnecessary HTML tags and links.
- Organize the content into logical chunks, including code examples.
- Output a CSV file containing structured information such as title, content, usage examples, category, tags, and reference URL.

The program is designed to streamline the process of converting raw HTML into a clean, organized dataset for further use in knowledge bases or other documentation tools.

---

## Key Features

1. **Dynamic Category Assignment**: The category column in the CSV is dynamically generated based on the last word in the provided URL.
2. **Reference URL**: Each document entry in the CSV includes the source URL as a reference.
3. **Data Organization**: Outputs a CSV file with fields such as `document_id`, `title`, `content`, `usage_example`, `category`, `tags`, and `reference`.
4. **Intermediate Steps**: Stores intermediate files at each processing step for easy debugging and reuse.

---

## Workflow

The program is split into multiple scripts, each handling a specific step in the workflow:

### 1. [simple_spider.py](lib/simple_spider.py)
- Fetches the HTML content from the provided URL.
- Extracts only the `<div class="td-content">` sections.
- Saves the raw HTML to an intermediate file in the `data/` folder.

### 2. [clean_html_links.py](lib/clean_html_links.py)
- Removes all `<a>` tags while keeping the text inside them.
- Outputs cleaned HTML content to an intermediate file in the `data/` folder.

### 3. [extract_h2.py](lib/extract_h2.py)
- Extracts `<h2>` sections along with their associated content.
- Organizes content into logical chunks based on headings.
- Outputs the extracted content to an intermediate file in the `data/` folder.

### 4. [extract_code_example.py](lib/extract_code_example.py)
- Extracts code blocks (`<code>` tags) from the HTML and evaluates which to keep based on specific conditions.
- Inserts placeholders for removed code blocks and appends kept code blocks for further processing.
- Saves the modified output to an intermediate file in the `data/` folder.

### 5. [clean_all_tags_and_newline.py](lib/clean_all_tags_and_newline.py)
- Removes all remaining HTML tags from the text.
- Ensures that each sentence ends with a newline for better readability.
- Outputs the cleaned content to an intermediate file in the `data/` folder.

### 6. [final_refine.py](lib/final_refine.py)
- Performs additional formatting and text refinements, such as handling edge cases.
- Prepares the text for CSV conversion.
- Outputs the refined text to an intermediate file in the `data/` folder.

### 7. [to_csv.py](lib/to_csv.py)
- Converts the fully processed text into a structured CSV file.
- Dynamically generates the `category` column based on the URL (e.g., `Kubernetes_ingress`).
- Includes the reference URL provided in the `Facade.py` as the `reference` column in the CSV.
- Saves the final CSV file as `final_output.csv` in the `data/` folder.

---

## Usage

### Running the Entire Workflow

You can run the entire workflow using the `Facade.py` script, which acts as the main entry point. It orchestrates all the individual scripts and manages intermediate files.

#### Command:
```bash
python3 Facade.py --url <website_url>
```
### Arguments:

#### `--url`:
- (Optional) The website URL to scrape. Defaults to Kubernetes Ingress documentation: https://kubernetes.io/docs/concepts/services-networking/ingress/

#### Example:
```bash
python3 Facade.py --url https://kubernetes.io/docs/concepts/services-networking/gateway/
```
### Output:

- The program creates a `data/` folder in the project directory to store all intermediate files.
- The final output CSV file is saved as: 
```bash
data/final_output.csv
```

