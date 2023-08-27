import logging
from bs4 import BeautifulSoup
from scraper.fetcher import fetch_page
import os
import requests
import time
import re

# scraper/parser.py

def parse_content(url, config):
    content = fetch_page(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        navbar_list = soup.select_one(config['navbar_list'])
        if not navbar_list:
            logging.error("Failed to find navbar list on the page.")
            return []

        navbar_items = navbar_list.select(config['navbar_item'])
        items = [(item.text.strip(), item.find('a')['href'] if item.find('a') else None) for item in navbar_items]  # Extracting both text and href

        # Grouping items
        grouped_items = {}
        parent_key = None
        for item_name, item_url in items:
            if '\n' in item_name:  # This indicates a parent category with sub-categories
                parent, *children = item_name.split('\n')
                # Remove duplicates and empty strings
                children = list(set(children))
                children = [(child, item_url) for child in children if child]  # Pairing child with URL
                if parent not in grouped_items:
                    grouped_items[parent] = children
                else:
                    grouped_items[parent].extend((child, item_url) for child in children if child not in [existing_child[0] for existing_child in grouped_items[parent]])
                parent_key = parent
            elif parent_key and item_name not in [existing_child[0] for existing_child in grouped_items[parent_key]]:
                grouped_items[parent_key].append((item_name, item_url))

        return grouped_items
    else:
        logging.error(f"Failed to retrieve content from {url}.")
        return []

def download_image(image_url, save_folder='downloaded_images'):
    """Download an image from the given URL and save it to the specified folder."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Create the save folder if it doesn't exist
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Use the original filename from the URL or generate one
        filename = os.path.join(save_folder, os.path.basename(image_url))

        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return filename  # Return path to saved image

    except requests.RequestException as e:
        print(f"Error downloading {image_url}. Error: {e}")
        return None


def scrape_products(url, config):
    logging.info(f"Starting scrape for URL: {url}")


    products = []
    content = fetch_page(url)

    if content:
        logging.info("Successfully fetched page content.")
        soup = BeautifulSoup(content, 'html.parser')
        product_elements = soup.select(config['product'])
        logging.info(f"Found {len(product_elements)} product elements.")

        for product_element in product_elements:
            product_url_element = product_element.select_one('a')  # Assuming the first 'a' tag is the product URL
            if product_url_element:
                product_url = product_url_element['href']
                product_details = scrape_individual_product(product_url, config)
                print(product_details)
                if product_details:
                    products.append(product_details)

        return products


import os
import re


def scrape_individual_product(url, config):
    content = fetch_page(url)
    if content:
        soup = BeautifulSoup(content, 'html.parser')

        # Extracting the product name using h1
        name_element = soup.select_one('h1')
        name = name_element.text.strip() if name_element else "N/A"

        # Extracting the entire content
        whole_content_element = soup.select_one(config['whole_content'])
        whole_content = whole_content_element.text.strip() if whole_content_element else "N/A"

        # Extracting price
        price_element = soup.select_one(config['price'])
        price = price_element.text.strip() if price_element else "N/A"

        # Extracting image
        image_element = soup.select_one('.attachment-large')
        if image_element:
            image_url = image_element['src']

        # Removing any size pattern from the image URL
        if image_element:
            image_url = re.sub(r'-\d+x\d+', '', image_element['src'])
        else:
            image_url = "N/A"

        # Extracting short description
        short_description_element = soup.find("meta", {"property": "og:description"})
        short_description = short_description_element["content"] if short_description_element else "N/A"

        # Extracting the long description
        long_description_element = soup.select_one('.elementor-widget-wrap')
        long_description = long_description_element.text.strip() if long_description_element else "N/A"

        # Downloading the image
        image_path = None
        if image_url != "N/A":
            file_extension = os.path.splitext(image_url)[1]
            unique_filename = f"{name}_{int(time.time())}{file_extension}"
            image_path = download_image(image_url, unique_filename)

        return {
            'name': name,
            'price': price,
            'image_url': image_url,
            'image_path': image_path,
            'short_description': short_description,
            'long_description': long_description,
            'whole_content': whole_content,
            'product_url': url
        }
    else:
        logging.error(f"Failed to retrieve content from {url}.")
        return None
