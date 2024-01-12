#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de parsing des fichiers d'entrée pour la mise en oeuvre du projet Poly#.
"""

from utils.Warehouse import Warehouse
from utils.Order import Order
from Challenge import Challenge

def parse_challenge(filename: str) -> object:
    """Lit un fichier de challenge et extrait les informations nécessaires.

    Vous pouvez choisir la structure de données structurées qui va
    représenter votre challenge: dictionnaire, objet, etc
    """
    with open(filename, 'r') as f:
        rows, columns, drone_count, deadline, max_load = [int(v) for v in f.readline().split()]
        f.readline()
        product_weights = [weight for weight in f.readline().split()]

        warehouse_count = int(f.readline())
        warehouse_list = []

        for id in range(warehouse_count):
            x, y = [int(v) for v in f.readline().split()]
            warehouse_products = [int(v) for v in f.readline().split()]
            warehouse_list.append(Warehouse(id, x, y, warehouse_products))

        order_count = int(f.readline())
        order_list = []

        for id in range(order_count):
            x, y = [int(v) for v in f.readline().split()]
            # Useless count of products in order
            f.readline()
            order_product = [int(v) for v in f.readline().split()]
            order_list.append(Order(id, x, y, order_product))

    challenge = Challenge(rows, columns, drone_count, deadline, max_load, product_weights, warehouse_list, order_list)
    
    return challenge
