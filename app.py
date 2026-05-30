from flask import Flask, render_template, send_file
import subprocess
import pandas as pd
import os

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

@app.route('/download')
def download():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)