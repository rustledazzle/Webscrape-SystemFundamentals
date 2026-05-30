import csv
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# ================= CONFIGURATION =================
EDGE_PROFILE_PATH = r"C:\Users\ruzz\AppData\Local\Microsoft\Edge\User Data"
SUBSCRIPTION_URL = "https://starlink.com/account/service-line/AST-2293597-46342-54?selectedDevice=ut01000000-00000000-0060d786&page=0&limit=5"
OUTPUT_CSV = "march_2026_daily_usage.csv"

# ================= SETUP =================
options = Options()
options.add_argument(f"--user-data-dir={EDGE_PROFILE_PATH}")
options.add_argument("--profile-directory=Default")
options.add_experimental_option("detach", True)

service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service, options=options)

# ================= HELPER FUNCTIONS =================
def click_tab(tab_text):
    print(f"🖱️ Clicking tab: '{tab_text}'")
    try:
        # Try exact text match first
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[.//h6[text()='{tab_text}']]"))
        )
        tab.click()
    except:
        # Fallback: button contains the text
        tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{tab_text}')]"))
        )
        tab.click()
    time.sleep(2)
    # Wait for chart to update (bars to reload)
    WebDriverWait(driver, 15).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, 'g[data-series="y_0"] rect')) > 0
    )
    print("   Tab clicked and chart updated.")

def get_y_axis_scale():
    """Read Y-axis labels (0 GB and top GB) and return GB per pixel."""
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
    
    zero_label = min_label
    top_label = max_label
    
    zero_y = zero_label.location['y']
    top_y = top_label.location['y']
    pixel_range = zero_y - top_y
    if pixel_range <= 0:
        raise Exception("Invalid Y-axis label positions")
    
    gb_per_pixel = max_num / pixel_range
    print(f"📊 Scale: {max_num} GB over {pixel_range:.1f} px → {gb_per_pixel:.6f} GB/px")
    return gb_per_pixel

def extract_bars_and_convert(gb_per_pixel):
    """Return list of daily usage (in order) from current chart."""
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'g[data-series="y_0"] rect'))
    )
    bars = driver.find_elements(By.CSS_SELECTOR, 'g[data-series="y_0"] rect[fill="#FFFFFF"]')
    if not bars:
        bars = driver.find_elements(By.CSS_SELECTOR, 'g[data-series="y_0"] rect')
    if not bars:
        raise Exception("No bars found")
    # Sort by x coordinate
    bars = sorted(bars, key=lambda b: float(b.get_attribute('x')))
    daily = []
    for bar in bars:
        height = float(bar.get_attribute('height'))
        gb = round(height * gb_per_pixel, 2)
        daily.append(gb)
    print(f"   Extracted {len(daily)} days. First 5: {daily[:5]}")
    return daily

# ================= MAIN =================
try:
    print("📡 Navigating to subscription page...")
    driver.get(SUBSCRIPTION_URL)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "svg.MuiChartsSurface-root"))
    )
    print("   Chart loaded.\n")

    # --- Scrape Feb-Mar period (Feb 17 – Mar 16) ---
    click_tab("Feb")          # Click the "Feb" button (shows Feb-Mar period)
    factor_feb = get_y_axis_scale()
    feb_mar_data = extract_bars_and_convert(factor_feb)
    print(f"   Feb-Mar: {len(feb_mar_data)} days extracted\n")

    # --- Scrape Mar-Apr period (Mar 17 – Apr 16) ---
    click_tab("Apr")          # Click the "Apr" button (shows Mar-Apr period)
    factor_apr = get_y_axis_scale()
    apr_data = extract_bars_and_convert(factor_apr)
    print(f"   Apr (Mar-Apr): {len(apr_data)} days extracted\n")

    # --- Combine for March 1-31 ---
    # Feb-Mar (30 days): last 16 entries are Mar 1-16
    # Mar-Apr (30 days): first 15 entries are Mar 17-31
    march_1_16 = feb_mar_data[-16:]   # last 16 entries
    march_17_31 = apr_data[:15]       # first 15 entries

    march_values = march_1_16 + march_17_31
    if len(march_values) != 31:
        print(f"⚠️ Warning: Expected 31 days, got {len(march_values)}. Check slicing.")
    else:
        # Generate dates and save CSV
        start_date = datetime(2026, 3, 1)
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'DataUsage_GB'])
            for i, usage in enumerate(march_values):
                date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
                writer.writerow([date, usage])
        print(f"✅ Combined March data saved to {OUTPUT_CSV}")
        print("\n📋 First 10 days of March:")
        for i in range(min(10, len(march_values))):
            print(f"   {march_values[i]} GB")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    input("\nPress Enter to close browser...")
    driver.quit()