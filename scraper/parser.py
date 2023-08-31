import logging
import os
import re
import time

from data.models.product import Product
from scraper.fetcher import web_driver_context

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import requests

logging.basicConfig(level=logging.INFO)


def parse_content(config):
    with web_driver_context(config['base_url']) as driver:
        all_products = []
        unique_product_links = set()

        try:
            # Extract navbar links
            navbar_links = extract_navbar_links(driver, config['navbar_item'])
            logging.info(f"Found {len(navbar_links)} links in the navbar.")

            for _, link in navbar_links:
                logging.info(f"Processing link: {link}")
                driver.get(link)

                while True:
                    # Capture initial product links
                    initial_product_links = extract_product_links(driver, config['product_list'])

                    # Try to click the "next" button to load more products
                    try:
                        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['Load_More_Button'])))
                        next_button.click()
                        time.sleep(5)  # Adjust this based on how long it takes for products to load
                    except TimeoutException:
                        # If "next" button is not found, break out of the loop
                        break

                    # Capture new product links after products have loaded
                    new_product_links = extract_product_links(driver, config['product_list'])

                    # If the product links haven't changed, break out of the loop
                    if set(initial_product_links) == set(new_product_links):
                        break

                    # Filter out duplicates and process new products
                    unique_new_product_links = set(new_product_links) - unique_product_links
                    unique_product_links.update(unique_new_product_links)

                    logging.info(f"Found {len(unique_new_product_links)} new unique product links on the page.")

                    for product_link in unique_new_product_links:
                        try:
                            driver.get(product_link)
                            product = extract_product_data(driver, config)
                            if product:
                                all_products.append(product)
                        except Exception as e:
                            logging.error(f"Error extracting data for product at {product_link}. Error: {e}")

        except Exception as e:
            logging.error(f"Error parsing content from {config['base_url']}. Error: {e}")
            return []

        logging.info(f"Scraping completed. Total products extracted: {len(all_products)}")
        return all_products

def group_items(items):
    """Group items based on their hierarchy."""
    grouped_items = {}
    parent_key = None

    for item_name, item_url in items:
        if '\n' in item_name:
            parent, *children = item_name.split('\n')
            children = list(set(children))
            children = [(child, item_url) for child in children if child]
            if parent not in grouped_items:
                grouped_items[parent] = children
            else:
                existing_children = [existing_child[0] for existing_child in grouped_items[parent]]
                grouped_items[parent].extend((child, item_url) for child in children if child not in existing_children)
            parent_key = parent
        elif parent_key:
            existing_children = [existing_child[0] for existing_child in grouped_items[parent_key]]
            if item_name not in existing_children:
                grouped_items[parent_key].append((item_name, item_url))

    return grouped_items

def get_elements_by_selector(driver, selector):
    """Return elements based on the provided CSS selector."""
    return driver.find_elements(By.CSS_SELECTOR, selector)

def extract_inner_html_and_href(elements):
    """Extract and clean innerHTML and href attributes from a list of elements."""
    return [
        (
            re.sub('<[^>]+>', '', element.get_attribute('innerHTML')).strip(),
            element.get_attribute('href')
        )
        for element in elements if element.get_attribute('href')
    ]

def extract_category_from_product_element(product_element):
    """Extract the category from a product element."""
    try:
        category_element = product_element.find_element(By.CSS_SELECTOR, '.jet-woo-product-categories a')
        return category_element.text
    except Exception as e:
        logging.error(f"Error extracting category. Error: {e}")
        return None

def extract_product_links(driver, selector):
    """Extract product URLs from the list of products."""
    product_elements = driver.find_elements(By.CSS_SELECTOR, selector + ' .jet-woo-product-thumbnail a')
    return [element.get_attribute('href') for element in product_elements]


def extract_product_data(driver, config):
    """Extract product data from a product element."""

    def get_element_text(selector):
        try:
            return driver.find_element(By.CSS_SELECTOR, selector).text
        except:
            return "N/A"

    def get_element_attribute(selector, attribute):
        try:
            return driver.find_element(By.CSS_SELECTOR, selector).get_attribute(attribute)
        except:
            return "N/A"

    name = get_element_text(config['name'])
    sku = get_element_text(config['SKU'])
    short_description = get_element_text(config['short_description'])
    long_description = get_element_text(config['long_description'])
    image_url = get_element_attribute(config.get('image', ''), 'src')
    #print('long_description: ', long_description)
    price = get_element_text(config.get('price', ''))

    return Product(name, sku, short_description, long_description, image_url, price)
def download_image(image_url, website_name, save_folder='downloaded_images'):
    """Download an image from the given URL and save it to the specified folder."""
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        directory_name = os.path.join(save_folder, website_name)
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)

        file_extension = os.path.splitext(image_url)[1]
        filename = f"{website_name}_{int(time.time())}{file_extension}"
        filepath = os.path.join(save_folder, website_name, filename)

        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return filepath

    except requests.RequestException as e:
        logging.error(f"Error downloading {image_url}. Error: {e}")
        return None

def extract_navbar_links(driver, selector):
    """Extract and clean navbar links."""
    navbar_links = driver.find_elements(By.CSS_SELECTOR, selector)
    return [
        (re.sub('<[^>]+>', '', link.get_attribute('innerHTML')).strip(), link.get_attribute('href'))
        for link in navbar_links if link.get_attribute('href') and not link.get_attribute('href').endswith('#')
    ]


def extract_image_url(soup, config):
    image_element = soup.select_one(config.get('image', ''))
    if image_element:
        return re.sub(r'-\d+x\d+', '', image_element['src'])
    return "N/A"


def download_image_if_exists(image_url, website_name):
    if image_url != "N/A":
        return download_image(image_url, website_name)
    return None


def handle_pagination(driver, config):
    """Clicks the "next" button until all products are loaded."""
    previous_num_products = 0
    while True:
        try:
            # Wait for the "next" button to be clickable
            wait = WebDriverWait(driver, 10)
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, config['Load_More_Button'])))


            # Check if the number of products has increased
            current_num_products = len(driver.find_elements(By.CSS_SELECTOR, config['product_list']))
            if current_num_products == previous_num_products:
                logging.info("No new products loaded. Exiting pagination loop.")
                break

            next_button.click()
            # Wait for products to load after clicking the button
            time.sleep(5)  # Adjust this based on how long it takes for products to load

            previous_num_products = current_num_products

        except TimeoutException:
            logging.info("Next button not found or not clickable. Exiting pagination loop.")
            break
        except Exception as e:
            logging.error(f"Error while clicking the 'next' button: {e}")
            break
