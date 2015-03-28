import sys
import traceback
import logging
import pickle
import io
from graph import Graph
from colony import Colony

def single_round(graph, num_ants, num_iterations):
    graph.reset_pheromone() # Reset pheromone to equally distributed
    workers = Colony(graph, num_ants, num_iterations)
    logging.debug("Colony Started")
    workers.start()
    return {'path': workers.best_path,
            'cost': workers.best_path_cost}

def cut_nodes(cost_matrix, num_nodes):
    """Cut off the distances we're not going to use in both dimensions (remove nodes from top level and from each city's array)"""
    if num_nodes >= len(cost_matrix):
        return cost_matrix

    cost_matrix = cost_matrix[0:num_nodes]
    for i in range(num_nodes):
        cost_matrix[i] = cost_matrix[i][0:num_nodes]
    return cost_matrix

def log_results(path):
    logging.info("Best path = %s", path['path'])
    logging.info(" ".join(path['names']))
    logging.info("Best path cost = %s", path['cost'])

def main(config):
    if config['nodes'] <= 10: # number of nodes to visit
        ants = 20 # number of ants
        iterations = 12 # number of iterations
        repetitions = 1 # number of repetitions of the entire algorithm
    else:
        ants = 28
        iterations = 20
        repetitions = 1

    data = io.read_input(config)
    cost_matrix = cut_nodes(data['costs'], config['nodes'])

    try:
        graph = Graph(config['nodes'], cost_matrix)
        best_path = None
        for i in range(0, repetitions):
            logging.info("Repetition %s", i)
            path = single_round(graph, ants, iterations)
            if  best_path is None or path['cost'] < best_path['cost']:
                logging.debug("Colony Path")
                best_path = path

        best_path['names'] = [data['nodes'][node] for node in best_path['path']]
        log_results(best_path)
        io.write_output(best_path, config)
    except Exception, e:
        logging.error("exception: " + str(e))
        traceback.print_exc()

if __name__ == "__main__":
    config = io.parse_args()
    main(config)
