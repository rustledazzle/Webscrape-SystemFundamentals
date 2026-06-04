import csv
import os
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("[INFO] Starting Edge browser with default profile")

# Path to your default Edge profile (Windows)
DEFAULT_PROFILE = os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data")
print(f"[INFO] Using default Edge profile at: {DEFAULT_PROFILE}")

# Configure Edge options to use the default profile
options = Options()
options.add_argument(f"--user-data-dir={DEFAULT_PROFILE}")
options.add_argument("--profile-directory=Default")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("detach", True)

# Use the LOCAL EdgeDriver you downloaded and renamed
# Make sure msedgedriver_143.exe is in the same folder as this script
service = Service(r"msedgedriver_143.exe")
driver = webdriver.Edge(service=service, options=options)

print(f"[INFO] Browser name: {driver.capabilities.get('browserName', 'unknown')}")
print(f"[INFO] Browser version: {driver.capabilities.get('browserVersion', 'unknown')}")

# ================= CONFIGURATION =================
SUBSCRIPTION_URL = "https://starlink.com/account/service-line/AST-2293597-46342-54?selectedDevice=ut01000000-00000000-0060d786&page=0&limit=5"
OUTPUT_CSV = "march_2026_daily_usage.csv"

# ================= HELPER FUNCTIONS =================
def click_tab(tab_text):
    print(f"[INFO] Clicking tab: '{tab_text}'")
    try:
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[.//h6[text()='{tab_text}']]"))
        )
        tab.click()
    except:
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{tab_text}')]"))
        )
        tab.click()
    time.sleep(2)
    WebDriverWait(driver, 15).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'g[data-series="y_0"] rect')) > 0
    )
    print("[INFO] Tab clicked and chart updated.")

def get_y_axis_scale():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiChartsAxis-left .MuiChartsAxis-tickLabel"))
    )
    labels = driver.find_elements(By.CSS_SELECTOR, ".MuiChartsAxis-left .MuiChartsAxis-tickLabel")
    gb_values = []
    for lbl in labels:
        text = lbl.text
        match = re.search(r"(\d+\.?\d*)\s*GB", text)
        if match:
            num = float(match.group(1))
            gb_values.append((num, lbl))
    if len(gb_values) < 2:
        raise Exception(f"Could not find at least two GB labels. Found: {[l.text for l in labels]}")
    max_num, max_label = max(gb_values, key=lambda x: x[0])
    min_num, min_label = min(gb_values, key=lambda x: x[0])
    zero_y = min_label.location['y']
    top_y = max_label.location['y']
    pixel_range = zero_y - top_y
    if pixel_range <= 0:
        raise Exception("Invalid Y-axis label positions")
    gb_per_pixel = max_num / pixel_range
    print(f"[INFO] Scale: {max_num} GB over {pixel_range:.1f} px -> {gb_per_pixel:.6f} GB/px")
    return gb_per_pixel

def extract_bars_and_convert(gb_per_pixel):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'g[data-series="y_0"] rect'))
    )
    bars = driver.find_elements(By.CSS_SELECTOR, 'g[data-series="y_0"] rect[fill="#FFFFFF"]')
    if not bars:
        bars = driver.find_elements(By.CSS_SELECTOR, 'g[data-series="y_0"] rect')
    if not bars:
        raise Exception("No bars found")
    bars = sorted(bars, key=lambda b: float(b.get_attribute('x')))
    daily = []
    for bar in bars:
        height = float(bar.get_attribute('height'))
        gb = round(height * gb_per_pixel, 2)
        daily.append(gb)
    print(f"[INFO] Extracted {len(daily)} days. First 5: {daily[:5]}")
    return daily

# ================= MAIN =================
def main():
    try:
        print("[INFO] Navigating to subscription page...")
        driver.get(SUBSCRIPTION_URL)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "svg.MuiChartsSurface-root"))
        )
        print("[INFO] Chart loaded.\n")

        click_tab("Feb")
        factor_feb = get_y_axis_scale()
        feb_mar_data = extract_bars_and_convert(factor_feb)
        print(f"[INFO] Feb-Mar: {len(feb_mar_data)} days extracted\n")

        click_tab("Apr")
        factor_apr = get_y_axis_scale()
        apr_data = extract_bars_and_convert(factor_apr)
        print(f"[INFO] Apr (Mar-Apr): {len(apr_data)} days extracted\n")

        march_1_16 = feb_mar_data[-16:]
        march_17_31 = apr_data[:15]
        march_values = march_1_16 + march_17_31

        if len(march_values) != 31:
            print(f"[WARN] Expected 31 days, got {len(march_values)}. Check slicing.")
        else:
            start_date = datetime(2026, 3, 1)
            with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'DataUsage_GB'])
                for i, usage in enumerate(march_values):
                    date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                    writer.writerow([date, usage])
            print(f"[INFO] Combined March data saved to {OUTPUT_CSV}")
            print("\n[INFO] First 10 days of March:")
            for i in range(min(10, len(march_values))):
                print(f"   {march_values[i]} GB")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
