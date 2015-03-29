import sys
import traceback
import logging
import pickle
import io
import graph as g
import colony as c

def single_round(workers):
    g.reset_pheromone(workers['graph']) # Reset pheromone to equally distributed
    c.reset(workers)
    c.run(workers)
    return {'path': workers['best_path']['path'],
            'cost': workers['best_path']['cost']}

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
    data = io.read_input(config)
    cost_matrix = cut_nodes(data['costs'], config['nodes'])
    colony_params = dict((param, config[param]) for param in ['alpha', 'beta', 'q0', 'rho', 'num_ants', 'iterations'])

    try:
        graph = g.create_graph(cost_matrix)
        workers = c.create_colony(graph, colony_params)
        logging.debug("Colony Started")
        best_path = None
        for i in range(0, config['repetitions']):
            logging.info("Repetition %s", i)
            path = single_round(workers)
            if  best_path is None or path['cost'] < best_path['cost']:
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
