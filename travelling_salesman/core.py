import math
import random

class Work():
    def __init__(self, ID, start_node, colony):
        self.ID = ID
        self.start_node = start_node
        self.colony = colony
        self.current_node = self.start_node
        self.graph = self.colony.graph
        self.path = []
        self.path.append(self.start_node)
        self.path_cost = 0
        self.Beta = 1.0
        self.Q0 = 0.5
        self.Rho = 0.99
        # map of city_id -> city_id, without start city
        # during transitions, the node that an ant moves to
        # is removed
        self.nodes_to_visit = {}
        for i in range(0, self.graph.num_nodes):
            if i != self.start_node:
                self.nodes_to_visit[i] = i
        self.path_matrix = []
        for i in range(0, self.graph.num_nodes):
            self.path_matrix.append([0] * self.graph.num_nodes)

    # move to new city found through state_transition_rule and remember the
    # distance. The new city is added to the path vector. The route is marked
    # on the path matrix.
    #could this be simpler?
    def run(self):
        graph = self.colony.graph
        while not self.end():
            new_node = self.state_transition_rule(self.current_node)
            self.path_cost += graph.distance(self.current_node, new_node)
            self.path.append(new_node)
            self.path_matrix[self.current_node][new_node] = 1
            self.local_updating_rule(self.current_node, new_node)
            self.current_node = new_node
        self.path_cost += graph.distance(self.path[-1], self.path[0])
        self.colony.update(self)
        self.__init__(self.ID, self.start_node, self.colony)

    def end(self):
        return not self.nodes_to_visit


    # Returns a city to move to using cost function
    # pheromone(current, next) * (1/dist(current, next))^beta (currently beta is always 1)
    def state_transition_rule(self, current_node):
        graph = self.colony.graph
        q = random.random() # in [0, 1]
        max_node = -1
        if q < self.Q0:
            # We will move to city with highest: pheromone*(1/distance)
            print "Exploitation"
            max_path_strength = -1
            path_strength = None
            for node in self.nodes_to_visit.values():
                if graph.pheromone(current_node, node) == 0:
                    raise Exception("pheromone = 0")
                path_strength = graph.pheromone(current_node, node) * math.pow(graph.inverse_distance(current_node, node), self.Beta)
                if path_strength > max_path_strength: # Remember city for highest pheromone path
                    max_path_strength = path_strength
                    max_node = node
        else:
            # Paper describes moving from current city c to a random city s with the probability
            # distribution p(s) = cost(c, s)/ sum of cost(c, r) over visited cities r
            # Here we find the average cost of travelling from c to all other not yet visited cities
            # and choose the last node that has a cost higher than the average. If none meet this criterion,
            # we choose the very last node
            #Bob was here
            print "Exploration"
            sum = 0
            node = -1
            for node in self.nodes_to_visit.values():
                if graph.pheromone(current_node, node) == 0:
                    raise Exception("pheromone = 0")
                sum += graph.pheromone(current_node, node) * math.pow(graph.inverse_distance(current_node, node), self.Beta)
            if sum == 0:
                raise Exception("sum = 0")
            avg = sum / len(self.nodes_to_visit)
            print "avg = %s" % (avg,)
            for node in self.nodes_to_visit.values():
                path_strength = graph.pheromone(current_node, node) * math.pow(graph.inverse_distance(current_node, node), self.Beta)
                if path_strength > avg:
                    print "path_strength = %s" % (path_strength,)
                    max_node = node
            if max_node == -1:
                max_node = node # Use last node
        if max_node < 0:
            raise Exception("max_node < 0")
        del self.nodes_to_visit[max_node]
        return max_node

    # Update the pheromone on the path to move towards the initial pheromone level,
    # which is inversely proportional to the number of cities and the average distance
    # New pheromone level is 0.01*old + 0.99*reset_pheromone
    def local_updating_rule(self, current_node, next_node):
        #Update the pheromones on the pheromone matrix to represent transitions of the ants
        graph = self.colony.graph
        new_strength = (1 - self.Rho) * graph.pheromone(current_node, next_node) + (self.Rho * graph.pheromone0)
        graph.update_pheromone(current_node, next_node, new_strength)


import random
import sys



class BigGroup:
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
        self.ants = self.create_workers()
        self.iteration = 0

        while self.iteration < self.num_iterations:
            self.perform_iteration()
            # Note that this will help refine the results future iterations.
            self.global_updating_rule()

    def perform_iteration(self):
        self.avg_path_cost = 0
        self.ant_counter = 0
        self.iteration += 1
        for ant in self.ants:
            ant.run()

    def num_ants(self):
        return len(self.ants)

    def num_iterations(self):
        return self.num_iterations

    def iteration_counter(self):
        return self.iteration

    def update(self, ant):
        print "Update called by %s" % (ant.ID,)
        self.ant_counter += 1
        self.avg_path_cost += ant.path_cost
        if ant.path_cost < self.best_path_cost:
            self.best_path_cost = ant.path_cost
            self.best_path_matrix = ant.path_matrix
            self.best_path = ant.path
            self.best_path_iteration = self.iteration
        if self.ant_counter == len(self.ants):
            self.avg_path_cost /= len(self.ants)
            print "Best: %s, %s, %s, %s" % (
                self.best_path, self.best_path_cost, self.iteration, self.avg_path_cost,)


    def done(self):
        return self.iteration == self.num_iterations

    def create_workers(self):
        self.reset()
        ants = []
        for i in range(0, self.num_ants):
            ant = Work(i, random.randint(0, self.graph.num_nodes - 1), self)
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

class GraphBit:
    def __init__(self, num_nodes, distance_matrix, pheromone_mat=None):
        print len(distance_matrix)
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
        print "Average = %s" % (avg,)
        print "pheromone0 = %s" % (self.pheromone0)
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
        graph = GraphBit(nodes_to_visit, cost_matrix)
        best_path = None
        best_path_cost = sys.maxint
        for i in range(0, repetitions):
            print "Repetition %s" % i
            graph.reset_pheromone() # Reset pheromone to equally distributed
            workers = BigGroup(graph, ants, iterations)
            print "Colony Started"
            workers.start()
            if workers.best_path_cost < best_path_cost:
                print "Colony Path"
                best_path = workers.best_path
                best_path_cost = workers.best_path_cost

        print "\n------------------------------------------------------------"
        print "                     Results                                "
        print "------------------------------------------------------------"
        print "\nBest path = %s" % (best_path,)
        path_by_names = []
        for node in best_path:
            print node_names[node] + " ",
            path_by_names.append(node_names[node])
        print "\nBest path cost = %s\n" % (best_path_cost,)
        results = [best_path, path_by_names, best_path_cost]
        pickle.dump(results, open(argv[2], 'w+'))
    except Exception, e:
        print "exception: " + str(e)
        traceback.print_exc()


if __name__ == "__main__":
    main(sys.argv[1:])
