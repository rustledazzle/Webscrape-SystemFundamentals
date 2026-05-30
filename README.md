# Starlink Daily Usage Scraper (March 2026)

This project scrapes daily data usage from a live Starlink account (provided by the professor) and presents it through a Flask web interface. It extracts March 2026 daily usage by automatically clicking the **Feb** and **Apr** tabs, reads the Y‑axis scale, converts bar heights to GB, and saves the data to a CSV file.

## Features

- **Automated login** – uses your existing Edge browser profile (no password stored).
- **Automatic tab switching** – clicks "Feb" (Feb–Mar period) and "Apr" (Mar–Apr period).
- **Dynamic Y‑axis scaling** – reads the chart's 0 GB and top GB labels to compute correct conversion.
- **Combines two periods** – extracts March 1–16 from Feb–Mar and March 17–31 from Mar–Apr.
- **Web UI** – buttons to run the scraper, view the data as an HTML table, and download the CSV.

## Prerequisites

- **Microsoft Edge** browser installed.
- **Python 3.8+** installed on your system.
- A logged‑in Starlink session in your Edge profile (the scraper reuses your existing cookies).

## How to Run (Windows)

1. **Download the project**  
   - Go to the GitHub repository page.  
   - Click the green **"Code"** button → **"Download ZIP"**.  
   - Extract the ZIP file to a folder on your computer, e.g., `C:\starlink_scraper`.

2. **Open a command prompt** (or PowerShell) in that folder:  
   - Navigate to the extracted folder.  
   - Click on the address bar, type `cmd`, and press Enter.

3. **Install the required Python packages**  
   In the command prompt, type:
   ```cmd
   pip install -r requirements.txt