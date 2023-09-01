import argparse
from scraper.parser import parse_content  # Import your main scraper function here

def list_websites():
    """List all available websites to scrape."""
    for website in WEBSITES.keys():
        print(website)

def scrape_website(website_name):
    """Scrape a specific website."""
    if website_name in WEBSITES:
        config = WEBSITES[website_name]
        parse_content(config)  # Call your scraper function with the specific config
    else:
        print(f"Website {website_name} not found!")

def scrape_all_websites():
    """Scrape all available websites."""
    for website_name, config in WEBSITES.items():
        parse_content(config)  # Call your scraper function with the specific config