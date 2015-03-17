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

