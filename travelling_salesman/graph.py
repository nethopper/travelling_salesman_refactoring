import logging
import pyrsistent as pst
from pyrsistent import m, v

def empty_matrix(size):
    return [[0 for x in range(size)] for y in range(size)]

def create_graph(distance_matrix, pheromone_matrix=None):
    num_nodes = len(distance_matrix)
    def rows_correct_size(matrix):
        return [len(row) == num_nodes for row in matrix]

    if not all(rows_correct_size(distance_matrix)):
        raise ValueError("The distance matrix must be square")
    elif pheromone_matrix is None:
        pheromone_matrix = empty_matrix(num_nodes)
    elif (len(pheromone_matrix) != num_nodes or
          not all(rows_correct_size(pheromone_matrix))):
        raise ValueError("The pheromone matrix must be the same size and shape as the distance matrix")

    return {'distances': distance_matrix,
            'pheromones': pheromone_matrix}

def inverse_distance(graph, start, end):
    return 1.0 / graph['distances'][start][end]

def size(graph):
    return len(graph['distances'])

def average(matrix):
    num_nodes = len(matrix)
    return sum(sum(row) for row in matrix) / float(num_nodes * num_nodes)

def base_pheromone(graph):
    return 1.0 / (size(graph) * 0.5 * average(graph['distances']))

def reset_pheromone(graph):
    num_nodes = size(graph)
    new_pheromones = [[base_pheromone(graph) for x in range(num_nodes)] for y in range(num_nodes)]
    graph['pheromones'] = new_pheromones
    return graph
