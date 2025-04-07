# 🕵️‍♂️ Private Equity Deal Scraper

This project provides two automated web scraping scripts for collecting **Private Equity deal information**. Input is fetched from a **Google Sheet**, and scraping is performed using `Selenium` with `undetected-chromedriver`. Results are saved to Excel files.

---

## 📁 Project Files

web-scraper/ ├── scraper_urls.py # Scrapes deals directly from Axial URLs in Google Sheet ├── scraper_deals_google.py # Searches firm names on Google and scrapes deals from matching pages ├── All_PE_Deals_URLs.xlsx # Output of deals scraped from Axial URLs ├── All_PE_Deals_Google.xlsx # Output of deals scraped via Google search └── README.md # Project documentation


---

## 🛠️ Requirements

Install the dependencies:

```bash
pip install pandas undetected-chromedriver selenium openpyxl
📝 Make sure Google Chrome is installed.

🔗 Input Source
Both scripts fetch data from this Google Sheet (as a CSV):

https://docs.google.com/spreadsheets/d/1JDYRh44C1-nvJb8t-Gsbvfp9eme72ZTF/export?format=csv&gid=1267470465
Required columns:

PE Firm
Axial Link (only needed for scraper_urls.py)

📘 Script 1: scraper_urls.py

✅ What it does:
Reads firm names and Axial links from Google Sheet
Visits each URL
Extracts deal information such as:
Title
Asking Price
Revenue
EBITDA
Deal Status (Sold, Available, etc.)
📤 Output:
Saves deals to:
All_PE_Deals_URLs.xlsx
▶️ Run it:
python scraper_urls.py

📘 Script 2: scraper_deals_google.py

✅ What it does:
Searches each PE firm on Google
Clicks the top result
Tries to find a "deals" or "portfolio" page
Extracts structured deal information
🔍 Keywords used:
To find deal pages: deals, portfolio, investments, acquisitions, etc.
📤 Output:
Saves deals to:

All_PE_Deals_Google.xlsx
▶️ Run it:
python scraper_deals_google.py
🧾 Output Format

Both scripts generate structured Excel files with the following columns:

PE Firm	Website	Title	Asking Price	Revenue	EBITDA	Status


👤 Author

Built by Supritha
