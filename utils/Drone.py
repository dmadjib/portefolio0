import math
class Drone:
    def __init__(self, drone_id, max_payload, initial_location):
        self.id = drone_id
        self.max_payload = max_payload
        self.current_location = initial_location
        self.current_load = 0
        self.available_turn = 0

    def available(self, current_turn):
        return current_turn >= self.available_turn

    def fly_to(self, location):
        distance = calculate_distance(self.current_location, location)
        self.available_turn += int(math.ceil(distance))

    def can_load(self, warehouse, product_type, quantity):
        total_weight = quantity * self.product_weights[product_type]
        return self.current_load + total_weight <= self.max_payload
    
    def load(self, warehouse, product_type, quantity, product_weights):
        total_weight = quantity * product_weights[product_type]
        self.current_load += total_weight
        warehouse.product_stock[product_type] -= quantity

    def deliver(self, order, product_type, quantity, product_weights):
        order.items[product_type] -= quantity
        self.current_load -= quantity * product_weights[product_type]

    def unload(self, warehouse, product_type, quantity, product_weights):
        total_weight = quantity * product_weights[product_type]
        self.current_load -= total_weight
        warehouse.product_stock[product_type] += quantity
    
def calculate_distance(location1, location2):
    return math.sqrt((location1[0] - location2[0]) ** 2 + (location1[1] - location2[1]) ** 2)
