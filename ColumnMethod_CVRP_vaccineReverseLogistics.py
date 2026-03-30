# -*- coding: utf-8 -*-

from networkx import (
    to_networkx_graph,
    set_node_attributes,
    relabel_nodes,
    DiGraph,
    compose,
)
from numpy import array
import pandas as pd
import numpy as np
import networkx as nx
from networkx import to_networkx_graph, DiGraph, relabel_nodes, set_node_attributes
from numpy import array
from vrpy.vrp import VehicleRoutingProblem
from vrpy import VehicleRoutingProblem
from json import dumps


def run_model_value(capacidad):
    
    DISTANCES = pd.read_excel("output2DistanciasSourceSink.xlsx",header=0)
    TIEMPOS_RECORRIDO = pd.read_excel("outputTiemposSourceSink.xlsx")
    DISTANCES2=DISTANCES.values.tolist()
    TRAVEL_TIMES = TIEMPOS_RECORRIDO.values.tolist()

    # Index for health centres
    counties = [*range(1,18)]
    #The * "unpacks" an iterable, so that each element is passed as a separate argument, rather than the function receiving the iterable object as a single argument:
    cantidadRecojo=[100,200,250,300,200,350,280,400,280,180,100,200,350,400,150,180,200,380,450]

    
    # Create a zip object from two lists
    DEMAND = zip(counties, cantidadRecojo)
    # Create a dictionary from zip object
    DEMAND = dict(DEMAND)

    COLLECT = {
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 2,
        6: 1,
        7: 4,
        8: 1,
        9: 1,
        10: 2,
        11: 3,
        12: 2,
        13: 4,
        14: 2,
        15: 1,
        16: 2,
    }

    DEMANDS_DROP = {
        0: 0,
        1: 1,
        2: 1,
        3: 3,
        4: 6,
        5: 3,
        6: 6,
        7: 8,
        8: 8,
        9: 1,
        10: 2,
        11: 1,
        12: 2,
        13: 6,
        14: 6,
        15: 8,
        16: 8,
    }

    TIME_WINDOWS_LOWER = {
        0: 1,
        1: 5,
        2: 5,
        3: 5,
        4: 5,
        5: 2,
        6: 5,
        7: 2,
        8: 5,
        9: 2,
        10: 10,
        11: 5,
        12:5,
        13:15,
        14:12,
        15:14,
        16:15,
        17:5,
    }

    TIME_WINDOWS_UPPER = {
        0: 65,
        1: 80,
        2: 75,
        3: 68,
        4: 63,
        5: 55,
        6: 70,
        7: 64,
        8: 50,
        9: 63,
        10: 76,
        11: 62,
        12:75,
        13:65,
        14:70,
        15:75,
        16:80,
        17:150,
    }

    PICKUPS_DELIVERIES = {
        (1, 6): 1,
        (2, 10): 2,
        (4, 3): 3,
        (5, 9): 1,
        (7, 8): 2,
        (15, 11): 3,
        (13, 12): 1,
        (16, 14): 4,
    }

   

    # The matrix is transformed into a DiGraph
    A = array(DISTANCES2, dtype=[("cost", int)])

    
    G = to_networkx_graph(A, create_using=nx.DiGraph())

   
    set_node_attributes(G, values=DEMAND, name="demand")

   
    G = relabel_nodes(G, {0: "Source", 18: "Sink"}) #el valor de 18 porque es la ultima columna

    #G.edges

    
    prob = VehicleRoutingProblem(G, load_capacity=capacidad, distribution_collection=True)
    prob.solve()
       
    #rutas = pd.DataFrame(prob._best_routes)
    #string=''.join([str(item) for item in prob._best_routes])
    converted = dumps(prob._best_routes)
    print(prob.best_value)
    print(prob._best_routes)

    return converted 

#This value changes for different Capacities to pick up on the sequence
capacidad = 600
# Returns Visit sequence and solves total distance*cost minimization
run_model_value(capacidad)
  
  
