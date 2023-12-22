import math
class Drone:
    def __init__(self, drone_id, max_payload, initial_location):
        self.id = drone_id
        self.max_payload = max_payload
        self.current_location = initial_location
        self.current_load = 0
        self.available_turn = 0
        self.products = {}

    def available(self, current_turn):
        return current_turn >= self.available_turn
    
    def can_load(self, product_type, quantity, product_weights):
        incoming_weight = quantity * int(product_weights[product_type])
        return self.current_load + incoming_weight <= self.max_payload
    
    def has_remaining(self, order):
        return all(self.has_product_asked(p, q) for p, q in order.products.items())
    
    def has_product_asked(self, product, quantity):
        return product in self.products and self.products[product] >= quantity

    def fly_to(self, location):
        distance = Drone.calculate_distance(self.current_location, location)
        self.available_turn += int(math.ceil(distance))
    
    def load(self, warehouse, product_type, quantity, product_weights, solutions):
        total_weight = quantity * int(product_weights[product_type])
        self.current_load += total_weight
        solutions.append([self.id, 'L', warehouse.id, product_type, quantity])
        
        try:
            self.products[product_type] += quantity
        except KeyError:
            self.products[product_type] = quantity

        warehouse.products[product_type] -= quantity

    def deliver(self, order, product_type, quantity, product_weights, solutions):
        order.products[product_type] -= quantity
        self.current_load -= quantity * int(product_weights[product_type])
        self.products[product_type] -= quantity
        solutions.append([self.id, 'D', order.id, product_type, quantity])
    
    @staticmethod
    def calculate_distance(location1, location2):
        return math.sqrt((location1[0] - location2[0]) ** 2 + (location1[1] - location2[1]) ** 2)
