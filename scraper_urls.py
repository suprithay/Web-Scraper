import os
import re
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === CONFIG ===
sheet_url = "https://docs.google.com/spreadsheets/d/1JDYRh44C1-nvJb8t-Gsbvfp9eme72ZTF/export?format=csv&gid=1267470465"
output_file = "All_PE_Deals_URLs.xlsx"

# === LOAD FIRMS AND LINKS ===
df = pd.read_csv(sheet_url)
if 'PE Firm' in df.columns and 'Axial Link' in df.columns:
    firms_links = df[['PE Firm', 'Axial Link']].dropna()
else:
    raise ValueError("❌ Required columns ('PE Firm', 'Axial Link') not found in Google Sheet!")

print("✅ Loaded PE Firms and URLs!")

# === SETUP SELENIUM ===
driver = uc.Chrome()
wait = WebDriverWait(driver, 10)

# === DEAL KEYWORDS & PATTERNS ===
status_keywords = ["under contract", "sold", "available", "pending"]
price_pattern = r"(Asking Price|Price|Purchase Price)[^\d$]*\$?\s?[\d,.]+[MBK]?"
revenue_pattern = r"(Revenue)[^\d$]*\$?\s?[\d,.]+[MBK]?"
ebitda_pattern = r"(EBITDA)[^\d$]*\$?\s?[\d,.]+[MBK]?"

# === STORAGE ===
all_deals = []

def extract_deals_from_page(firm_name, url):
    driver.get(url)
    time.sleep(3)
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
            "Website": url,
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
for _, row in firms_links.iterrows():
    firm = row['PE Firm']
    link = row['Axial Link']

    print(f"\n🌐 Visiting: {firm} => {link}")
    try:
        before_count = len(all_deals)
        extract_deals_from_page(firm, link)
        after_count = len(all_deals)

        if after_count > before_count:
            save_progress()
        else:
            print(f"📭 No deals found on {link}")
    except Exception as e:
        print(f"⚠️ Error processing {firm}: {e}")
        continue

driver.quit()
print("\n🚀 Scraping complete!")