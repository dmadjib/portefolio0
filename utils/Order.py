class Order:

    def __init__(self, id, x, y, products) -> None:
        self.id = id
        self.location = (x, y)
        self.amount = len(products)
        self.products = {product_type: products.count(product_type) for product_type in products}

    def is_completed(self):
        return all(q == 0 for q in self.products.values())
