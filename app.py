from flask import Flask, render_template, send_file, jsonify
import subprocess
import pandas as pd
import os
import csv

app = Flask(__name__)
CSV_FILE = "march_2026_daily_usage.csv"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape')
def scrape():
    # Run your scraping script (make sure it's in the same folder)
    subprocess.run(["python", "scrape_march_complete.py"])
    return "Scraping completed!"

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
        # Convert to list of {date, usage}
        data = [{'date': row['Date'], 'usage': float(row['DataUsage_GB'])} for row in rows]
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([])  # empty list if CSV not yet generated

@app.route('/download')
def download():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
