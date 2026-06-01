# Starlink Daily Usage Scraper (March 2026)

This project scrapes daily data usage from a live Starlink account using **Microsoft Edge** and displays the results through a Flask web interface. It automatically extracts March 1–31, 2026 daily usage by clicking the **Feb** and **Apr** tabs, reading the Y‑axis scale, and converting bar heights to GB.

## Features

- **Automatic login** – uses your existing Edge profile (no password stored).
- **No manual path configuration** – automatically finds your Edge profile folder.
- **Auto‑scale detection** – reads chart labels (0 GB and top GB) to convert bar heights accurately.
- **Combines two periods** – extracts March 1–16 from Feb–Mar tab and March 17–31 from Mar–Apr tab.
- **Web UI** – buttons to run the scraper, view data as a table, and download CSV.

## Requirements

- Windows 10/11
- Microsoft Edge browser (installed in default location)
- Python 3.8 or higher
- You must be **already logged into Starlink** in your Edge profile (manual login once).

## Installation

1. **Download the repository** (ZIP or `git clone`).
2. Open a command prompt in the project folder.
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
