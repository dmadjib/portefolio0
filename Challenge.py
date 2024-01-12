from utils.Drone import Drone
class Challenge:
    def __init__(self, rows_count, columns_count, drone_count,deadline,max_payload,product_weights,warehouses,orders):
        self.rows_count = rows_count
        self.columns_count = columns_count
        self.drone_count = drone_count
        self.deadline = deadline
        self.max_payload = max_payload
        self.product_weights = product_weights
        self.warehouses = warehouses
        self.orders = orders
        self.drones = []
        for i in range(drone_count):
            self.drones.append(Drone(i,self.max_payload,self.warehouses[0].location))

