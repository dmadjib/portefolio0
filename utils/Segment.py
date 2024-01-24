"""
@title : Segment
@description : Class defining what a segment is
@author : El ARAJNA Lina , FAKHFAKH Ahmed , LALANNE-TISNE Nino, Madjibaye Donatien
@date : Last Modification : 20/01/2024
"""

from utils.Drone import Drone
import math

class Segment:
    """
        Class is defined by:
            - start
            - end
            - challenge
            - actions
        """

    """ Constructor """

    def __init__(self, start, end, challenge, actions, order_id) -> None:
        self.order_id = order_id
        self.start = start
        self.end = end
        self.actions = actions
        self.turns = self.calcul_turns(challenge)

    """ Static Method """
    @staticmethod
    def get_location(action, challenge):
        """
            - Get the location of the warehouse or the order
            :return:        The location of the warehouse if the action is 'L' or 'U',
                            the location of the order if the action is not 'L' or 'U'
        """
        if action[1] in {'L', 'U'}:
            return list(filter(lambda w:w.id == action[2], challenge.warehouses))[0].location
        else:
            return list(filter(lambda o:o.id == action[2], challenge.orders))[0].location

    def calcul_turns(self, challenge):
        """
            - Calculate the turns of a challenge
            :return:        The turns
        """
        turns = 0

        pos = self.start

        for action in self.actions:
            # Recuperate the location of the action
            location = Segment.get_location(action, challenge)
            # Add turns for movement (after deposit / charge)
            turns += Drone.calculate_distance(pos, location) + 1
            # Update the location of the drone
            pos = location

        return turns