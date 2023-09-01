class Product:
    def __init__(self, name, sku, category, short_description, long_description, image_url, price, product_url=None):
        self.name = name
        self.sku = sku
        self.category = category
        self.short_description = short_description
        self.long_description = long_description
        self.image_url = image_url
        self.price = price
        self.product_url = product_url

    def __repr__(self):
        return f"<Product(name={self.name}, sku={self.sku}, category={self.category}, price={self.price})>"

    def display(self):
        return f"Name: {self.name}\nSKU: {self.sku}\nPrice: {self.price}\n..."

    def serialize(self):
        return {
            'name': self.name,
            'sku': self.sku,
            'category': self.category,
            'short_description': self.short_description,
            'long_description': self.long_description,
            'image_url': self.image_url,
            'price': self.price,
            'product_url': self.product_url
        }
    # You can also add any other methods or utility functions related to the Product class here.
