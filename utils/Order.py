class Order:
    def __init__(self, order_id, delivery_location, item_count, items):
        self.id = order_id
        self.delivery_location = delivery_location
        self.item_count = item_count
        self.items = {product_type: items.count(product_type) for product_type in set(items)}