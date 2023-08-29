from scraper.parser import parse_content, scrape_products
from config.settings import WEBSITES
from scraper.storage import save_to_csv

def main():
    for website, config in WEBSITES.items():
        print(f"Scraping data for {website} using the following configuration: {config}")
        url = config['base_url']
        categories = parse_content(url, config)

        # Check if categories is empty
        if not categories:
            print(f"No categories found for {website}. Moving to the next website.")
            continue

        # Scrape products for each category
        all_products = []
        for category, sub_categories in categories.items():
            for sub_category_name, sub_category_url in sub_categories:
                print(f"Scraping products for sub-category: {sub_category_name}")
                products = scrape_products(sub_category_url, config)
                for product in products:
                    product['category'] = category
                    product['sub_category'] = sub_category_name
                all_products.extend(products)

        # Save the scraped data to a CSV file only if there are products
        if all_products:
            filename = f"{website}_scraped_data.csv"
            save_to_csv(all_products, filename)
        else:
            print(f"No products found for {website}. Skipping CSV creation.")

if __name__ == "__main__":
    main()
