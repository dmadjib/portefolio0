from utils.Drone import Drone
import math

class Segment:

    def __init__(self, start, end, challenge, actions, order_id, index) -> None:
        self.order_id = order_id
        self.start = start
        self.end = end
        self.actions = actions
        self.turns = self.calcul_turns(challenge, index)

    @staticmethod
    def get_location(action, challenge, index):
        return challenge.warehouses[action[index]].location if action[1] in {'L', 'U'} else challenge.orders[action[index]].location

    def calcul_turns(self, challenge, index):
        turns = 0

        pos = self.start

        for action in self.actions:
            # Récupérer la localisation de l'action
            location = Segment.get_location(action, challenge, index)
            # Ajout des tours pour le déplacement (après dépôt / charge)
            turns += Drone.calculate_distance(pos, location) + 1
            # Mise à jour de la localisation du drone
            pos = location

        return turns