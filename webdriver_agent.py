import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from openpyxl import Workbook
from datetime import datetime
import time
import schedule

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

BASE_URL = "https://www.axial.net/forum/companies/united-states-m-a-advisory-firms/"


def scrape_website(url, page_number):
    try:
        print(f"Fetching content from {url}...")
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        articles = soup.find_all('article', class_='teaser1')
        print(f"Found {len(articles)} articles on page {page_number}.")

        data = []
        for index, article in enumerate(articles):
            title_tag = article.find('h4', class_='teaser1-title')
            description_tag = article.find('div', class_='teaser1-description')

            title = title_tag.get_text(strip=True) if title_tag else 'N/A'
            link = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else None
            description = description_tag.get_text(strip=True) if description_tag else 'N/A'

            data.append({
                'title': title,
                'link': link,
                'description': description,
                'page': page_number
            })

        return data

    except Exception as e:
        print(f"Error scraping page {page_number}:", e)
        return []


def create_excel_sheet(data, filename, foldername):
    if not data:
        print("No data to save.")
        return

    if not os.path.exists(foldername):
        os.makedirs(foldername)

    filepath = os.path.join(foldername, filename)
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False)
    print(f"Excel file '{filepath}' has been created.")


def scrape_all_pages():
    print("Starting full scrape...")
    all_data = []

    for page in range(1, 5):
        url = BASE_URL + (f"{page}" if page > 1 else "")
        page_data = scrape_website(url, page)
        all_data.extend(page_data)
        time.sleep(2)  # Avoid hammering the server

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    create_excel_sheet(all_data, f"Advisory_Firms_{timestamp}.xlsx", "Advisory_Firms")
    print("Scraping complete.")


def schedule_scraping():
    schedule.every(1).minutes.do(scrape_all_pages)
    print("Scheduler started. Waiting for the next job...")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    scrape_all_pages()  # Initial scrape
    schedule_scraping()  # Then schedule future scrapes
