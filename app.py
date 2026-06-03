from flask import Flask, render_template, send_file, jsonify
import subprocess
import pandas as pd
import os
import csv
import sys

app = Flask(__name__)
CSV_FILE = "march_2026_daily_usage.csv"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    script_path = os.path.join(os.path.dirname(__file__), "scrape_march_complete.py")
    print(f"[FLASK] Running scraper: {script_path}")
    
    # Use sys.executable to ensure same Python interpreter
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True,
        timeout=120
    )
    print("[FLASK] STDOUT:\n", result.stdout)
    print("[FLASK] STDERR:\n", result.stderr)
    
    if result.returncode != 0:
        return f"Scraping failed with code {result.returncode}. Check terminal for details."
    return "Scraping completed! Check terminal for details."

@app.route('/data')
def data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        return df.to_html(index=False)
    return "No data yet. Run scrape first."

@app.route('/data_json')
def data_json():
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        data = [{'date': row['Date'], 'usage': float(row['DataUsage_GB'])} for row in rows]
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([])

@app.route('/download')
def download():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
