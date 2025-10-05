# Internship Job Extractor

This project contains a set of Python scripts designed to parse internship listings from Markdown files, filter for relevant software roles, clean the data, and merge the results into a single, deduplicated CSV file.

## Features

- Parses job listings from both Markdown and HTML table formats.
- Filters roles by a customizable list of keywords (e.g., 'Software Engineer', 'SWE', 'Backend').
- Converts relative post dates (like '3d' or '1mo') to a standard `YYYY-MM-DD` format.
- Cleans data by removing tracking parameters from URLs and filtering out non-US locations.
- Merges multiple CSV files and removes duplicate entries based on the unique job application link.

## Data Source

The primary input files (`.md`) for this project are sourced from the following repositories:

- [SimplifyJobs/Summer2026-Internships](https://github.com/SimplifyJobs/Summer2026-Internships)
- [vanshb03/Summer2026-Internships (dev branch)](https://github.com/vanshb03/Summer2026-Internships/tree/dev)

## How to Use

### 1\. Requirements

First, ensure you have Python 3 installed. Then, install the necessary libraries from the `requirements.txt` file. It's recommended to use a virtual environment.

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install required packages
pip install -r requirements.txt
```

### 2\. Step 1: Parse a New Job List

Use the `internship.py` script to parse a source `.md` file downloaded from the repositories above. This will create a new, clean CSV file containing only the filtered software jobs.

Following job openings are removing:

- 🛂 Does NOT offer sponsorship
- 🇺🇸 Requires U.S. Citizenship
- 🔒 Internship application is closed
- 🎓 Advanced degree required (Master's, PhD, MBA)

**Usage:**

```bash
python internship.py <input_file.md> -o <output_file.csv>
```

**Example:**

```bash
python internship.py "C:\Users\JohnLee\Downloads\jobs.md" -o new_software_jobs.csv
```

### 3\. Step 2: Merge with a Master List

Use the `merge_csv.py` script to combine the newly created CSV file with your master list (e.g., `software_jobs.csv`). The script will automatically handle duplicates, ensuring the final list contains only unique job postings.

**Usage:**

```bash
python merge_csv.py <new_jobs.csv> <master_list.csv> -o <updated_master_list.csv>
```

**Example:**

```bash
# Merge the new jobs with your existing master list
python merge_csv.py new_software_jobs.csv software_jobs.csv -o software_jobs_updated.csv

# You can then overwrite the old master list with the updated one
# mv software_jobs_updated.csv software_jobs.csv (on macOS/Linux)
# move software_jobs_updated.csv software_jobs.csv (on Windows)
```
