import csv
import os
import requests

def save_to_csv(data, filename="scraped_data.csv"):
    # Define the path to save the file based on your project structure
    save_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_data', filename)

    with open(save_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(["Website", "Name", "Price", "Category", "Sub-Category", "Image URL", "Image Path", "Short Description", "Long Description"])  # Updated headers

        # Check if data is a dictionary and handle accordingly
        if isinstance(data, dict):
            for entry in data:
                writer.writerow([
                    "contipet.co.il",
                    entry.get('name', 'N/A'),
                    entry.get('price', 'N/A'),
                    entry.get('category', 'N/A'),
                    entry.get('sub_category', 'N/A'),
                    entry.get('image_url', 'N/A'),
                    entry.get('image_path', 'N/A'),
                    entry.get('short_description', 'N/A'),
                    entry.get('long_description', 'N/A')
                ])

        # If data is a list, write it based on your initial structure
        elif isinstance(data, list):
            for item in data:
                writer.writerow([
                    "contipet.co.il",
                    item.get('name', 'N/A'),
                    item.get('price', 'N/A'),
                    item.get('category', 'N/A'),
                    item.get('sub_category', 'N/A'),
                    item.get('image_url', 'N/A'),
                    item.get('image_path', 'N/A'),
                    item.get('short_description', 'N/A'),
                    item.get('long_description', 'N/A')
                ])


def download_image(url, product_name):
    img_data = requests.get(url).content
    image_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'product_images', f"{product_name}.jpg")
    with open(image_path, 'wb') as handler:
        handler.write(img_data)
    return url, image_path  # Return both the image URL and the path to the saved image

def store_products(products):
    for product in products:
        # save product data to CSV or database
        if product['image_url'] != "N/A":
            image_url, image_path = download_image(product['image_url'], product['name'])
            product['image_url'] = image_url
            product['image_path'] = image_path  # Add the image path to the product dictionary
    save_to_csv(products)  # Save the products with the image paths to the CSV
