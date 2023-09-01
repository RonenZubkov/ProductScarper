import os
import csv

def save_to_csv(products, file_path):
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['name', 'sku', 'category', 'short_description', 'long_description', 'image_url', 'price', 'product_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product in products:

            writer.writerow({
                'name': getattr(product, 'name', 'N/A'),
                'sku': getattr(product, 'sku', 'N/A'),
                'category': getattr(product, 'category', 'N/A'),
                'short_description': getattr(product, 'short_description', 'N/A'),
                'long_description': getattr(product, 'long_description', 'N/A'),
                'product_url': getattr(product, 'product_url', 'N/A'),
                'image_url': getattr(product, 'image_url', 'N/A'),
                'price': getattr(product, 'price', 'N/A')
            })
