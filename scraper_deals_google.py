import os
import re
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIG ===
sheet_url = "https://docs.google.com/spreadsheets/d/1JDYRh44C1-nvJb8t-Gsbvfp9eme72ZTF/export?format=csv&gid=1267470465"
output_file = "All_PE_Deals.xlsx"

# === LOAD FIRMS ===
df = pd.read_csv(sheet_url)
if 'PE Firm' in df.columns:
    firm_names = df['PE Firm'].dropna().tolist()
else:
    raise ValueError("❌ 'PE Firm' column not found in Google Sheet!")
print("✅ Loaded PE Firm Names!")

# === SETUP SELENIUM ===
driver = uc.Chrome()
wait = WebDriverWait(driver, 10)

# === DEAL KEYWORDS ===
deal_keywords = ["deals", "portfolio", "investments", "businesses", "opportunities", "for sale", "acquisitions"]
status_keywords = ["under contract", "sold", "available", "pending"]
price_pattern = r"(Asking Price|Price|Purchase Price)[^\d$]*\$?\s?[\d,.]+[MBK]?"
revenue_pattern = r"(Revenue)[^\d$]*\$?\s?[\d,.]+[MBK]?"
ebitda_pattern = r"(EBITDA)[^\d$]*\$?\s?[\d,.]+[MBK]?"

# === DEAL STORAGE ===
all_deals = []

# === FUNCTIONS ===
def search_google_and_get_website(firm_name):
    driver.get("https://www.google.com/")
    search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
    search_box.clear()
    search_box.send_keys(firm_name)
    search_box.send_keys(Keys.RETURN)
    try:
        first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3")))
        first_result.click()
        time.sleep(3)
        return driver.current_url
    except Exception as e:
        print(f"❌ Could not find site for {firm_name}: {e}")
        return None

def navigate_to_deals_page():
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        try:
            text = link.text.lower()
            if any(keyword in text for keyword in deal_keywords):
                href = link.get_attribute("href")
                if href and href.startswith("http"):
                    driver.get(href)
                    time.sleep(3)
                    return True
        except:
            continue
    return False

def extract_deals_from_page(firm_name, base_url):
    page_text = driver.find_element(By.TAG_NAME, "body").text
    deal_blocks = re.split(r'\n{2,}', page_text)

    for block in deal_blocks:
        title = block.strip().split("\n")[0][:80]
        price = re.search(price_pattern, block, re.IGNORECASE)
        revenue = re.search(revenue_pattern, block, re.IGNORECASE)
        ebitda = re.search(ebitda_pattern, block, re.IGNORECASE)
        status = next((word for word in status_keywords if word in block.lower()), "Not Found")

        deal = {
            "Firm": firm_name,
            "Website": base_url,
            "Title": title,
            "Asking Price": price.group(0) if price else "Not Found",
            "Revenue": revenue.group(0) if revenue else "Not Found",
            "EBITDA": ebitda.group(0) if ebitda else "Not Found",
            "Status": status.capitalize() if status != "Not Found" else "Not Found",
        }

        if any(v != "Not Found" for k, v in deal.items() if k not in ["Firm", "Website", "Title"]):
            all_deals.append(deal)
            print(f"📦 Found deal: {deal['Title']}")

def save_progress():
    df_deals = pd.DataFrame(all_deals)
    df_deals.to_excel(output_file, index=False)
    print(f"💾 Saved progress to {output_file} ({len(all_deals)} deals total)")

# === MAIN LOOP ===
for firm in firm_names:
    print(f"\n🔍 Searching: {firm}")
    firm_url = search_google_and_get_website(firm)
    if not firm_url:
        continue

    if not navigate_to_deals_page():
        print(f"❌ No deals/portfolio page found for {firm_url}")
        continue

    try:
        before_count = len(all_deals)
        extract_deals_from_page(firm, firm_url)
        after_count = len(all_deals)

        if after_count > before_count:
            save_progress()
        else:
            print(f"📭 No deals found for {firm}.")
    except Exception as e:
        print(f"⚠️ Error scraping {firm}: {e}")
        continue

driver.quit()
print("\n🚀 Scraping complete!")
