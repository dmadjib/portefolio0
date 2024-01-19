from utils.Drone import Drone
import math

class Segment:

    def __init__(self, start, end, challenge, actions) -> None:
        self.start = start
        self.end = end
        self.actions = actions
        self.turns = self.calcul_turns(challenge)

    @staticmethod
    def get_location(action, challenge):
        return challenge.warehouses[action[2]].location if action[1] in {'L', 'U'} else challenge.orders[action[2]].location

    def calcul_turns(self, challenge):
        turns = 0

        pos = self.start

        for action in self.actions:
            # Récupérer la localisation de l'action
            location = Segment.get_location(action, challenge)
            # Ajout des tours pour le déplacement (après dépôt / charge)
            turns += math.ceil(Drone.calculate_distance(pos, location)) + 1
            # Mise à jour de la localisation du drone
            pos = location

        return turns