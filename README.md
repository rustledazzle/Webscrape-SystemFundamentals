# Starlink Daily Usage Scraper (March 2026)

This project scrapes daily data usage from a live Starlink account using **Microsoft Edge** and presents the results through a Flask web interface. It automatically extracts March 1–31, 2026 daily usage by clicking the **Feb** and **Apr** tabs, reading the Y‑axis scale, and converting bar heights to GB.

## Features

- **Automatic login** – uses your existing Edge profile (no password stored).
- **No manual path configuration** – automatically finds your Edge profile folder.
- **Auto‑scale detection** – reads chart labels (0 GB and top GB) to convert bar heights accurately.
- **Combines two periods** – extracts March 1–16 from Feb–Mar tab and March 17–31 from Mar–Apr tab.
- **Web UI** – buttons to run the scraper, view data as a table and bar chart, and download CSV.

## Requirements

- Windows 10/11 (the script is designed for Windows)
- Microsoft Edge browser installed in the default location
- Python 3.8 or higher
- You must be **already logged into Starlink** in your Edge profile (manual login once)

## Installation

1. **Download the repository** (ZIP from GitHub or clone with Git).
2. Open a **Command Prompt** in the project folder.
3. Install the required Python packages:
   ```cmd
   pip install -r requirements.txt

Usage
Start the Flask web interface
In the same command prompt/terminal, run:

    py app.py
Open your browser and go to http://127.0.0.1:5000.

Scrape the data
Click the "Run Scraper & Show Data" button.

A new Edge window will open using your logged‑in Starlink profile.

The script will automatically click the Feb tab, wait for the chart to load, extract the Feb–Mar data, then click the Apr tab, and extract the Mar–Apr data.

After combining the data, the table and bar chart on the web page will update with the daily usage for March 1–31.

The CSV file march_2026_daily_usage.csv is saved in the project folder.

Download the CSV
Click the "Download CSV" button to save the file locally.
      
            starlink_scraper/
            ├── app.py                         # Flask application (routes: /, /scrape, /data, /data_json, /download)
            ├── scrape_march_complete.py       # Main scraping script (Selenium + BeautifulSoup)
            ├── templates/
            │   └── index.html                 # Web interface (dark theme, chart, table)
            ├── requirements.txt               # Python dependencies
            ├── march_2026_daily_usage.csv     # Generated output (example)
            └── README.md                      # This file
         

## Troubleshooting
Edge WebDriver version mismatch – Update Edge to the latest version, or download the matching EdgeDriver manually from Microsoft Edge WebDriver and place msedgedriver.exe in the project folder.

Edge profile not found – The script automatically detects your Edge profile. If it fails, open Edge, go to edge://version/, copy the Profile Path, and update the EDGE_PROFILE_PATH variable in scrape_march_complete.py.

No data loaded – Make sure you are logged into Starlink in your Edge profile before running the scraper.

## Important Notes
The scraper works with the Feb and Apr tabs. If your Starlink page uses different tab texts (e.g., "Feb – Mar"), adjust the click_tab() arguments in scrape_march_complete.py.

The script assumes each period has exactly 30 days. If the number of bars differs, you may need to adjust the slicing (feb_mar_data[-16:], apr_data[:15]) in the main script.
