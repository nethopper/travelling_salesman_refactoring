import logging
import pyrsistent as pst
from pyrsistent import m, v

def to_persistent(matrix):
    return pst.pvector(pst.pvector(row) for row in matrix)

def empty_matrix(size):
    return v(v(0) * size) * size

def create_graph(distance_matrix, pheromone_matrix=None):
    num_nodes = len(distance_matrix)
    def rows_correct_size(matrix):
        return [len(row) == num_nodes for row in matrix]

    if not all(rows_correct_size(distance_matrix)):
        raise ValueError("The distance matrix must be square")
    elif pheromone_matrix is None:
        pheromones = empty_matrix(num_nodes)
    elif (len(pheromone_matrix) != num_nodes or
          not all(rows_correct_size(pheromone_matrix))):
        raise ValueError("The pheromone matrix must be the same size and shape as the distance matrix")
    else:
        pheromones = to_persistent(pheromone_matrix)
    distances = to_persistent(distance_matrix)

    return m(distances = distances,
             pheromones = pheromones)

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
    new_pheromones = v(v(base_pheromone(graph)) * num_nodes) * num_nodes
    return graph.set('pheromones', new_pheromones)
