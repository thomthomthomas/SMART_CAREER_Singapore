# How to Use the Modified Web Scraper

This document explains how to use the updated `tavily_web_scraper.py` script.

## Overview of Changes

The script has been modified to:

1.  **Consolidate Modules**: Course modules are now extracted and placed directly under the `modules` key for each website, rather than nested within individual courses.
2.  **Fix Website Naming**: The `website_name` field now extracts a cleaner, more readable name from the URL.
3.  **Callable Function**: The main scraping logic is now encapsulated in a `run_scraper` function, making it easy to import and use in other Python files.
4.  **Search Toggle**: A `search_all` parameter has been added to the `run_scraper` function. Setting this to `True` will search all provided websites; setting it to `False` (default) will only search the first website in the list.

## Usage

### 1. Running the Script Directly

You can run the script directly from your terminal as before. The `if __name__ == "__main__":` block demonstrates how to use the new `run_scraper` function.

```bash
python3.11 tavily_web_scraper.py
```

This will run the scraper with the predefined `test_skills` and `test_websites` (searching all websites by default) and save the output to `website_modules_output.json`.

### 2. Using as a Callable Function

You can import `run_scraper` into another Python file and call it with your desired parameters.

**Example: `my_app.py`**

```python
import os
from tavily_web_scraper import run_scraper

# Set your API keys (recommended via environment variables)
os.environ["TAVILY_API_KEY"] = "YOUR_TAVILY_API_KEY"
os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"

# Define your skills and websites
my_skills = ["Data Science"]
my_websites = [
    "https://www.datacamp.com",
    "https://www.kaggle.com"
]

# Run the scraper, searching only the first website
print("\n--- Searching only the first website ---")
run_scraper(skills=my_skills, websites=my_websites, search_all=False, output_filename="data_science_modules_single.json")

# Run the scraper, searching all websites
print("\n--- Searching all websites ---")
run_scraper(skills=my_skills, websites=my_websites, search_all=True, output_filename="data_science_modules_all.json")
```

### Parameters for `run_scraper`:

*   `skills` (List[str]): A list of skills to search for (e.g., `["Python programming"]`).
*   `websites` (List[str]): A list of website URLs to scrape (e.g., `["https://www.coursera.org"]`).
*   `search_all` (bool, optional): If `True`, searches all websites in the `websites` list. If `False` (default), searches only the first website. Defaults to `False`.
*   `output_filename` (str, optional): The name of the JSON file to save the results to. Defaults to `website_modules_output.json`.

## API Keys

Ensure your `TAVILY_API_KEY` and `GEMINI_API_KEY` are set as environment variables or directly in the `run_scraper` function (as shown in the example for `GEMINI_API_KEY` in the `tavily_web_scraper.py` file).

