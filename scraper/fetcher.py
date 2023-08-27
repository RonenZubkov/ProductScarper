# scraper/fetcher.py

import requests
from config.settings import BASE_URL, HEADERS, TIMEOUT
import logging

logging.basicConfig(level=logging.INFO)

def fetch_page(url=BASE_URL):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.Timeout:
        logging.error(f"Timeout error for URL: {url}")
    except requests.RequestException as e:
        logging.error(f"Error fetching the page {url}. Error: {e}")
    return None