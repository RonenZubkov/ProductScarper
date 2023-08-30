import requests
import logging
from config.settings import BASE_URL, HEADERS, TIMEOUT
from selenium.webdriver.chrome.service import Service
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)

"""
def create_session():
    session = requests.Session()

    # Retry strategy
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )

    # Mount the session with the retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def fetch_with_session(url, delay=5):
    with create_session() as session:
        try:
            time.sleep(delay)
            response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException:
            return None


def fetch_directly(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def fetch_with_custom_user_agent(url):
    custom_headers = HEADERS.copy()
    custom_headers[
        "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    try:
        response = requests.get(url, headers=custom_headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None



"""


"""

def fetch_page(url=BASE_URL):
    with requests.Session() as session:
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        try:
            time.sleep(2)  # Delay for 5 seconds
            response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.Timeout:
            logging.error(f"Timeout error for URL: {url}")
        except requests.RequestException as e:
            logging.error(f"Error fetching the page {url}. Error: {e}")
        return None


"""
logging.basicConfig(level=logging.INFO)

from contextlib import contextmanager

@contextmanager
def web_driver_context(url):

    capabilities = {
        'browserName': 'chrome',
        'platform': 'ANY',
        'version': '',
    }

    options = Options()
    options.headless = True
    options.set_capability("browserName", "chrome")
    service = Service(executable_path=r'C:\Users\ronen\PycharmProjects\Product Scarper\bin\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    try:
        yield driver
    finally:
        driver.quit()

def fetch_page(url=BASE_URL):
    print(f"Attempting to navigate to: {url}")
    with web_driver_context(url) as driver:
        return driver.page_source

