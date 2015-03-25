import sys
import traceback
import logging
import pickle
import argparse
from graph import Graph
from colony import Colony

def parse_args(args):
    """Parse input arguments, returning a map of their values. This function should take into account any default values or overrides."""
    parser = argparse.ArgumentParser(description='Solve a Travelling Salesman Problem using an Ant Colont Optimization algorithm.')
    parser.add_argument('input_file', metavar='input_file', type=str,
                        help='Path to the input file')
    parser.add_argument('output_file', metavar='output_file', type=str,
                        help='Path to the output file')
    parser.add_argument('nodes_to_visit', metavar='nodes_to_visit', type=int,
                        help='The number of nodes to visit', default=10, nargs='?')
    return parser.parse_args(args)

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

def output_results(path, filename):
    results = [path['path'], path['names'], path['cost']]
    pickle.dump(results, open(filename, 'w+'))

def log_results(path):
    logging.info("Best path = %s", path['path'])
    logging.info(" ".join(path['names']))
    logging.info("Best path cost = %s", path['cost'])

def main(config):
    if config['nodes_to_visit'] <= 10: # number of nodes to visit
        ants = 20 # number of ants
        iterations = 12 # number of iterations
        repetitions = 1 # number of repetitions of the entire algorithm
    else:
        ants = 28
        iterations = 20
        repetitions = 1

    [node_names, cost_matrix] = pickle.load(open(config['input_file'], "r"))
    cost_matrix = cut_nodes(cost_matrix, config['nodes_to_visit'])

    try:
        graph = Graph(config['nodes_to_visit'], cost_matrix)
        best_path = None
        for i in range(0, repetitions):
            logging.info("Repetition %s", i)
            path = single_round(graph, ants, iterations)
            if  best_path is None or path['cost'] < best_path['cost']:
                logging.debug("Colony Path")
                best_path = path

        best_path['names'] = [node_names[node] for node in best_path['path']]
        log_results(best_path)
        output_results(best_path, config['output_file'])
    except Exception, e:
        logging.error("exception: " + str(e))
        traceback.print_exc()

if __name__ == "__main__":
    config = parse_args(sys.argv)
    main(config)
