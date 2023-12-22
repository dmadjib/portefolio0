#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module de résolution du projet Poly#.
"""
from utils.Drone import Drone
from utils.Order import Order
from utils.Warehouse import Warehouse
 
def save_solution (file_name, tab_solution) : 
    
    with open(f'{file_name}.txt', 'w') as outfile :
        outfile.write(str(len(tab_solution)) + '/n')
        for i in range(len(tab_solution)) : 
            for j in range(len(tab_solution[i])) :
                outfile.write(tab_solution[i][j] + ' ')
            outfile.write('/n')

def solve(challenge):
    pass