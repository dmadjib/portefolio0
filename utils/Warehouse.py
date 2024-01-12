class Warehouse:

    def __init__(self, id, x, y, products) -> None:
        self.id = id
        self.location = (x, y)
        self.products = products