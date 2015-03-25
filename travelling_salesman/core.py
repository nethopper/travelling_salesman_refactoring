import sys
import traceback
import logging
import pickle
from graph import Graph
from colony import Colony

def parse_args(argv):
    if len(argv) < 3:
        argv.insert(0, 10)
    return {'nodes_to_visit': int(argv[0]),
            'input_file': argv[1],
            'output_file': argv[2]}

def single_round(graph, num_ants, num_iterations):
    graph.reset_pheromone() # Reset pheromone to equally distributed
    workers = Colony(graph, num_ants, num_iterations)
    logging.debug("Colony Started")
    workers.start()
    return {'path': workers.best_path,
            'cost': workers.best_path_cost}

def cut_cities(cost_matrix, num_nodes):
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

def main(argv):
    config = parse_args(argv)

    if config['nodes_to_visit'] <= 10: # number of nodes to visit
        ants = 20 # number of ants
        iterations = 12 # number of iterations
        repetitions = 1 # number of repetitions of the entire algorithm
    else:
        ants = 28
        iterations = 20
        repetitions = 1

    [node_names, cost_matrix] = pickle.load(open(config['input_file'], "r"))
    cost_matrix = cut_cities(cost_matrix, config['nodes_to_visit'])

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
    main(sys.argv[1:])
