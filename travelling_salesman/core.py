import math
import random
import logging
from copy import deepcopy

class Ant():
    def __init__(self, ID, start_node, graph):
        self.ID = ID
        self.start_node = start_node
        self.current_node = self.start_node
        self.graph = graph
        self.path = [self.start_node]
        self.path_cost = 0
        self.Beta = 1.0
        self.Q0 = 0.5
        self.Rho = 0.99
        self.reset_nodes_to_visit()
        self.reset_path_matrix()

    def reset_nodes_to_visit(self):
        # map of city_id -> city_id, without start city
        # during transitions, the node that an ant moves to
        # is removed
        self.nodes_to_visit = [n for n in range(self.graph.num_nodes) if n != self.start_node]


    def reset_path_matrix(self):
        self.path_matrix = [[0] * self.graph.num_nodes] * self.graph.num_nodes


    # move to new city found through state_transition_rule and remember the
    # distance. The new city is added to the path vector. The route is marked
    # on the path matrix.
    #could this be simpler?
    def run(self):
        while not self.end():
            self.extend_path()
        self.add_cost_of_return()
        return {'ID': self.ID,
                'path_cost':  self.path_cost,
                'path_matrix': deepcopy(self.path_matrix),
                'path': deepcopy(self.path)}

    def extend_path(self):
        new_node = self.state_transition_rule(self.current_node)
        self.path_cost += self.graph.distance(self.current_node, new_node)
        self.path.append(new_node)
        self.path_matrix[self.current_node][new_node] = 1
        self.local_updating_rule(self.current_node, new_node)
        self.current_node = new_node

    def add_cost_of_return(self):
        self.path_cost += self.graph.distance(self.path[-1], self.path[0])

    def end(self):
        return not self.nodes_to_visit

    # Returns a city to move to using cost function
    # pheromone(current, next) * (1/dist(current, next))^beta (currently beta is always 1)
    def state_transition_rule(self, current_node):
        max_node = None
        if self.should_use_exploitation():
            max_node = self.exploit_best_edge(current_node)
        else:
            max_node = self.explore_random_edge(current_node)
        if max_node is None:
            raise Exception("max_node not found")
        self.nodes_to_visit.remove(max_node)
        return max_node

    def should_use_exploitation(self):
        return random.random() < self.Q0

    def exploit_best_edge(self, current_node):
        # We will move to city with highest: pheromone*(1/distance)
        logging.debug("Exploitation")
        strength_to = lambda node : self.path_strength(current_node, node)
        return max(self.nodes_to_visit, key=strength_to)

    # Paper describes moving from current city c to a random city s with the probability
    # distribution p(s) = cost(c, s)/ sum of cost(c, r) over visited cities r
    # Here we find the average cost of travelling from c to all other not yet visited cities
    # and choose the last node that has a cost higher than the average. If none meet this criterion,
    # we choose the very last node
    def explore_random_edge(self, current_node):
        logging.debug("Exploration")
        max_node = self.nodes_to_visit[-1]

        avg_strength = sum(self.path_strength(current_node, node) for node in self.nodes_to_visit) / len(self.nodes_to_visit)

        logging.debug("avg = %s", avg_strength)

        is_eligible = lambda n: self.path_strength(current_node, n) > avg_strength
        eligible_nodes = filter(is_eligible, self.nodes_to_visit)

        if eligible_nodes:
            return eligible_nodes[-1]
        else:
            return self.nodes_to_visit[-1]

    def path_strength(self, start, end):
        return self.graph.pheromone(start, end) * math.pow(self.graph.inverse_distance(start, end), self.Beta)

    # Update the pheromone on the path to move towards the initial pheromone level,
    # which is inversely proportional to the number of cities and the average distance
    # New pheromone level is 0.01*old + 0.99*reset_pheromone
    def local_updating_rule(self, current_node, next_node):
        #Update the pheromones on the pheromone matrix to represent transitions of the ants
        new_strength = (1 - self.Rho) * self.graph.pheromone(current_node, next_node) + (self.Rho * self.graph.pheromone0)
        self.graph.update_pheromone(current_node, next_node, new_strength)


import random
import sys

class Colony:
    def __init__(self, graph, num_ants, num_iterations):
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.Alpha = 0.1
        self.reset()

    def reset(self):
        self.best_path_cost = sys.maxint             # best path cost (length)
        self.best_path = None                   # best path vector
        self.best_path_matrix = None                   # best path matrix
        self.best_path_iteration = 0                     # last best path iteration

    def start(self):
        self.reset()
        self.iteration = 0

        while self.iteration < self.num_iterations:
            self.ants = self.create_workers()
            self.perform_iteration()
            # Note that this will help refine the results future iterations.
            self.global_updating_rule()

    def perform_iteration(self):
        self.avg_path_cost = 0
        self.ant_counter = 0
        self.iteration += 1
        for ant in self.ants:
            self.update(ant.run())


    def num_ants(self):
        return len(self.ants)

    def num_iterations(self):
        return self.num_iterations

    def iteration_counter(self):
        return self.iteration

    def update(self, ant):
        logging.debug("Update called by %s", ant['ID'])
        self.ant_counter += 1
        self.avg_path_cost += ant['path_cost']
        if ant['path_cost'] < self.best_path_cost:
            self.best_path_cost = ant['path_cost']
            self.best_path_matrix = ant['path_matrix']
            self.best_path = ant['path']
            self.best_path_iteration = self.iteration
        if self.ant_counter == len(self.ants):
            self.avg_path_cost /= len(self.ants)
            logging.debug("Best: %s, %s, %s, %s",
                          self.best_path, self.best_path_cost, self.iteration, self.avg_path_cost)


    def done(self):
        return self.iteration == self.num_iterations

    def create_workers(self):
        ants = []
        for i in range(0, self.num_ants):
            ant = Ant(i, random.randint(0, self.graph.num_nodes - 1), self.graph)
            ants.append(ant)

        return ants

    def global_updating_rule(self):
        #can someone explain this
        evaporation = 0
        deposition = 0
        for start in range(0, self.graph.num_nodes):
            for end in range(0, self.graph.num_nodes):
                if start != end:
                    delt_pheromone = self.best_path_matrix[start][end] / self.best_path_cost # This is 0 if start->end is not on current best path
                    evaporation = (1 - self.Alpha) * self.graph.pheromone(start, end) # 10% of pheromone evaporates
                    deposition = self.Alpha * delt_pheromone # deposition inversely proportional to total path length
                    self.graph.update_pheromone(start, end, evaporation + deposition)

class Graph:
    def __init__(self, num_nodes, distance_matrix, pheromone_mat=None):
        logging.debug(len(distance_matrix))
        if len(distance_matrix) != num_nodes:
            raise Exception("len(distance) != num_nodes")
        self.num_nodes = num_nodes
        self.distance_matrix = distance_matrix # distance matrix
        if pheromone_mat is None:
            self.pheromone_mat = []  # init as matrix of 0s with a row and column for each city
            for i in range(0, num_nodes):
                self.pheromone_mat.append([0] * num_nodes)

    # Distance between cities r and s
    def distance(self, r, s):
        return self.distance_matrix[r][s]

    # Amount of pheromone between cities r and s
    def pheromone(self, r, s):
        return self.pheromone_mat[r][s]

    def inverse_distance(self, r, s):
        return 1.0 / self.distance(r, s)

    def update_pheromone(self, r, s, val):
        self.pheromone_mat[r][s] = val

    # Init amount of pheromone between all cities to be the same
    # The amount is inversely proportional to the number of cities
    # and the average distance between cities.
    def reset_pheromone(self):
        avg = self.average_distance()
        self.pheromone0 = 1.0 / (self.num_nodes * 0.5 * avg)
        logging.debug("Average = %s", avg)
        logging.debug("pheromone0 = %s", self.pheromone0)
        for start in range(0, self.num_nodes):
            for end in range(0, self.num_nodes):
                self.pheromone_mat[start][end] = self.pheromone0


    # Average distance between cities
    def average_distance(self):
        return self.average(self.distance_matrix)


    def average_pheromone(self):
        return self.average(self.pheromone_mat)

    def average(self, matrix):
        sum = 0
        for start in range(0, self.num_nodes):
            for end in range(0, self.num_nodes):
                sum += matrix[start][end]

        avg = sum / (self.num_nodes * self.num_nodes)
        return avg

import pickle
import sys
import traceback


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
