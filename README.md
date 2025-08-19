# Indian Sign Language (ISL) Video Dataset Scraper

A Python-based web scraper for extracting Indian Sign Language video data from [TalkingHands.co.in](https://talkinghands.co.in) for research, machine learning, and accessibility projects.

***

## Features

- **Automatic Category Discovery:** Dynamically finds all ISL categories available on the site.
- **Video and Metadata Extraction:** Retrieves all word/sign entries, collects video URLs and durations.
- **Organized Output:** Generates structured Excel (`.xlsx`) files for each category and the complete dataset.
- **Progress Backups:** Saves after each category to ensure incremental progress.
- **Error Handling:** Captures screenshots and logs detailed errors for debugging.
- **Headless and Visible Browser Support:** Choose between silent scraping (`app.py`) or debugging mode (`main.py`).

***

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/silentone12725/Dataset-scraper.git
   cd Dataset-scraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > Required packages: `requests`, `beautifulsoup4`, `pandas`, `selenium`, `openpyxl`

3. **Prepare ChromeDriver**
   - Download and place [ChromeDriver](https://chromedriver.chromium.org/downloads) in your system PATH.

***

## Usage

### For headless operation (recommended):
```bash
python app.py
```

### For debugging (visible browser window):
```bash
python main.py
```

Excel data will be saved in the `output/` directory.

***

## Output Format

Each dataset contains:

| Name            | yt_name | Link                     | start_min | start_sec | end_min | end_sec |
|-----------------|---------|--------------------------|-----------|-----------|---------|---------|
| Word/Sign name  | Word/Sign name | Video URL           | Start minutes | Start seconds | End minutes | End seconds |

- **Category files:** `isl_dataset_[CategoryName].xlsx`
- **Progress file:** `isl_dataset_progress.xlsx` (updates after every category)
- **Full dataset:** `isl_dataset_complete.xlsx`

***

## Scripts

- **`app.py`:** Main scraper with robust error handling and headless Chrome operation.
- **`main.py`:** Variant for browser-based debugging.
- **`requirements.txt`:** All Python package dependencies.

***

## Tips and Troubleshooting

- **Slow or Unstable Network:** The scraper includes short delays to be polite to servers; ensure a stable connection.
- **ChromeDriver Issues:** Verify ChromeDriver version matches your Chrome browser.
- **Incomplete Data:** Website structure changes may require script updates.
- **Permission Errors:** Make sure you have write access for the `output` directory.

***

## Legal/Ethical Notes

- Use only for research and educational purposes.
- Respect [TalkingHands.co.in](https://talkinghands.co.in) and its terms of service.
- Do not flood or abuse the site; the script implements basic rate-limiting.

***

## Contributing

Open to issues, suggestions, and improvements via GitHub.

***

## License

Distributed for research and education. Ensure you comply with third-party website terms and copyright when using scraped content.

---
