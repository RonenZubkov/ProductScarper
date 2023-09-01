from scraper.parser import parse_content
from config.settings import WEBSITES
from scraper.storage import save_to_csv
import subprocess
import psutil
import os
import argparse
import requests
from scraper.fetcher import web_driver_context
from scraper.utils import save_to_csv
from cli import list_websites, scrape_website, scrape_all_websites

def is_chromedriver_running():
    """Check if ChromeDriver is running and return its PID."""
    for process in psutil.process_iter():
        try:
            pinfo = process.as_dict(attrs=['pid', 'name'])
            if "chromedriver" in pinfo['name']:
                return pinfo['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None

def start_chromedriver():
    """Start ChromeDriver."""
    cmd = [r"C:\Users\ronen\PycharmProjects\Product Scarper\bin\chromedriver.exe", "--port=4444"]
    try:
        subprocess.Popen(cmd)
    except Exception as e:
        print(f"Error starting ChromeDriver: {e}")

def test_chromedriver_connection():
    """Test if we can connect to the ChromeDriver server."""
    try:
        response = requests.get('http://127.0.0.1:4444/wd/hub/status')
        if response.status_code == 200:
            print("Successfully connected to ChromeDriver!")
        else:
            print("Failed to connect to ChromeDriver.")
    except requests.RequestException as e:
        print(f"Error connecting to ChromeDriver: {e}")


def main():
    chromedriver_pid = is_chromedriver_running()
    if not chromedriver_pid:
        start_chromedriver()
    else:
        print(f"ChromeDriver is already running with PID {chromedriver_pid}.")

    # Display available websites
    print("Available websites to scrape:")
    for idx, website in enumerate(WEBSITES.keys(), 1):
        print(f"{idx}. {website}")
    print(f"{len(WEBSITES) + 1}. All websites")

    # Get user choice
    choice = int(input("Enter the number of the website you want to scrape (or choose 'All websites'): "))

    if choice == len(WEBSITES) + 1:  # User chose "All websites"
        websites_to_scrape = WEBSITES.keys()
    else:
        selected_website = list(WEBSITES.keys())[choice - 1]
        websites_to_scrape = [selected_website]

    for website in websites_to_scrape:
        config = WEBSITES[website]
        print(f"Scraping data for {website} using the following configuration: {config}")

        # Fetch navbar links
        products = parse_content(config)

        # If navbar_links is empty, move to the next website
        if not products:
            print(f"No navbar links found for {website}. Moving to the next website.")
            continue

        # After scraping, create a directory for the website and save the products
        directory_name = website.replace('.', '_')  # replace dots with underscores

        # Create directory if it doesn't exist
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        # Save the products to a CSV file inside the directory
        save_to_csv(products, os.path.join('data\\raw_data', directory_name, "products.csv"))


if __name__ == "__main__":
    main()