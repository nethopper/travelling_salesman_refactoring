import sys
import traceback
import logging
import pickle
from graph import Graph
from colony import Colony

def main(argv):
    nodes_to_visit = 10

    if len(argv) >= 3 and argv[0]:
        nodes_to_visit = int(argv[0])

    if nodes_to_visit <= 10: # number of nodes to visit
        ants = 20 # number of ants
        iterations = 12 # number of iterations
        repetitions = 1 # number of repetitions of the entire algorithm
    else:
        ants = 28
        iterations = 20
        repetitions = 1

    input_data = pickle.load(open(argv[1], "r"))
    node_names = input_data[0]
    cost_matrix = input_data[1] # distances for each city
    #why are we doing this?
    if nodes_to_visit < len(cost_matrix):
        # cut off the distances we're not going to use
        # in both dimensions (remove nodes from top level
        # and from each city's array)
        cost_matrix = cost_matrix[0:nodes_to_visit]
        for i in range(0, nodes_to_visit):
            cost_matrix[i] = cost_matrix[i][0:nodes_to_visit]



    try:
        graph = Graph(nodes_to_visit, cost_matrix)
        best_path = None
        best_path_cost = sys.maxint
        for i in range(0, repetitions):
            logging.info("Repetition %s", i)
            graph.reset_pheromone() # Reset pheromone to equally distributed
            workers = Colony(graph, ants, iterations)
            logging.debug("Colony Started")
            workers.start()
            if workers.best_path_cost < best_path_cost:
                logging.debug("Colony Path")
                best_path = workers.best_path
                best_path_cost = workers.best_path_cost

        logging.info("Best path = %s", best_path)
        path_by_names = []
        for node in best_path:
            path_by_names.append(node_names[node])
        logging.info(" ".join(path_by_names))
        logging.info("Best path cost = %s", best_path_cost)
        results = [best_path, path_by_names, best_path_cost]
        pickle.dump(results, open(argv[2], 'w+'))
    except Exception, e:
        logging.error("exception: " + str(e))
        traceback.print_exc()


if __name__ == "__main__":
    main(sys.argv[1:])
