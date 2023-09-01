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
            # Extract navbar links and ensure uniqueness
            navbar_links = set(extract_navbar_links(driver, config['navbar_item']))
            logging.info(f"Found {len(navbar_links)} unique links in the navbar.")

            for _, link in navbar_links:
                logging.info(f"Processing link: {link}")
                driver.get(link)
                handle_pagination(driver, config)  # Moved pagination handling to a separate function

                # Capture product links
                product_links = extract_product_links(driver, config['product_list'])

                # Filter out duplicates and process new products
                unique_new_product_links = set(product_links) - unique_product_links
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

def extract_product_links(driver, selector):
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
    sku = re.sub(r'\D', '', get_element_text(config['SKU']))
    short_description = get_element_text(config['short_description'])
    long_description = get_element_text(config['long_description'])
    image_url = get_element_attribute(config.get('image', ''), 'src')
    price = get_element_text(config.get('price', ''))
    category = get_element_text(config.get('category', ''))
    product_url = str(driver.current_url)

    return Product(
        name=name,
        sku=sku,
        category=category,
        short_description=short_description,
        long_description=long_description,
        image_url=image_url,
        price=price,
        product_url=product_url
    )

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


