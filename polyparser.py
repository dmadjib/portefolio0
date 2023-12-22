#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de parsing des fichiers d'entrée pour la mise en oeuvre du projet Poly#.
"""

from utils.Warehouse import Warehouse
from utils.Order import Order

def parse_challenge(filename: str) -> object:
    """Lit un fichier de challenge et extrait les informations nécessaires.

    Vous pouvez choisir la structure de données structurées qui va
    représenter votre challenge: dictionnaire, objet, etc
    """
    with open(filename, 'r') as f:
        rows, columns, drone_count, deadline, max_load = [int(v) for v in f.readline().split()]
        product_count = int(f.readline())
        product_weights = [weight for weight in f.readline().split()]

        warehouse_count = int(f.readline())
        warehouse_list = []

        for _ in range(warehouse_count):
            x, y = [int(v) for v in f.readline().split()]
            warehouse_products = [int(v) for v in f.readline().split()]
            warehouse_list.append(Warehouse(x, y, warehouse_products))

        order_count = int(f.readline())
        order_list = []

        for _ in range(order_count):
            order_list.append()


    return challenge
