import csv

def save_to_csv(products, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'sku', 'category', 'short_description', 'long_description', 'image_url', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product in products:
            writer.writerow(product.__dict__)