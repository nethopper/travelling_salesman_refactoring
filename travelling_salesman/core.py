import math
import random

class Work():
    def __init__(self, ID, start_node, colony):
        self.ID = ID
        self.start_node = start_node
        self.grouping = colony
        self.curr_node = self.start_node
        self.graph = self.grouping.graph
        self.path_vec = []
        self.path_vec.append(self.start_node)
        self.path_cost = 0
        self.Beta = 1.0
        self.Q0 = 0.5
        self.Rho = 0.99
        # map of city_id -> city_id, without start city
        # during transitions, the node that an ant moves to
        # is removed
        self.ntv = {}
        for i in range(0, self.graph.num_nodes):
            if i != self.start_node:
                self.ntv[i] = i
        self.path_mat = []
        for i in range(0, self.graph.num_nodes):
            self.path_mat.append([0] * self.graph.num_nodes)

    # move to new city found through state_transition_rule and remember the
    # distance. The new city is added to the path vector. The route is marked
    # on the path matrix.
    #could this be simpler?
    def run(self):
        graph = self.grouping.graph
        while not self.end():
            new_node = self.state_transition_rule(self.curr_node)
            self.path_cost += graph.delta(self.curr_node, new_node)
            self.path_vec.append(new_node)
            self.path_mat[self.curr_node][new_node] = 1
            self.local_updating_rule(self.curr_node, new_node)
            self.curr_node = new_node
        self.path_cost += graph.delta(self.path_vec[-1], self.path_vec[0])
        self.grouping.update(self)
        self.__init__(self.ID, self.start_node, self.grouping)

    def end(self):
        return not self.ntv


    # Returns a city to move to using cost function
    # pheromone(current, next) * (1/dist(current, next))^beta (currently beta is always 1)
    def state_transition_rule(self, curr_node):
        graph = self.grouping.graph
        q = random.random() # in [0, 1]
        max_node = -1
        if q < self.Q0:
            # We will move to city with highest: pheromone*(1/distance)
            print "Exploitation"
            max_val = -1
            val = None
            for node in self.ntv.values():
                if graph.tau(curr_node, node) == 0:
                    raise Exception("tau = 0")
                val = graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
                if val > max_val: # Remember city for highest pheromone path
                    max_val = val
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
            for node in self.ntv.values():
                if graph.tau(curr_node, node) == 0:
                    raise Exception("tau = 0")
                sum += graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
            if sum == 0:
                raise Exception("sum = 0")
            avg = sum / len(self.ntv)
            print "avg = %s" % (avg,)
            for node in self.ntv.values():
                p = graph.tau(curr_node, node) * math.pow(graph.etha(curr_node, node), self.Beta)
                if p > avg:
                    print "p = %s" % (p,)
                    max_node = node
            if max_node == -1:
                max_node = node # Use last node
        if max_node < 0:
            raise Exception("max_node < 0")
        del self.ntv[max_node]
        return max_node

    # Update the pheromone on the path to move towards the initial pheromone level,
    # which is inversely proportional to the number of cities and the average distance
    # New pheromone level is 0.01*old + 0.99*reset_tau
    def local_updating_rule(self, curr_node, next_node):
        #Update the pheromones on the tau matrix to represent transitions of the ants
        graph = self.grouping.graph
        val = (1 - self.Rho) * graph.tau(curr_node, next_node) + (self.Rho * graph.tau0)
        graph.update_tau(curr_node, next_node, val)


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
        self.bpc = sys.maxint             # best path cost (length)
        self.bpv = None                   # best path vector
        self.bpm = None                   # best path matrix
        self.lbpi = 0                     # last best path iteration

    def start(self):
        self.ants = self.c_workers()
        self.iter_counter = 0

        while self.iter_counter < self.num_iterations:
            self.iteration()
            # Note that this will help refine the results future iterations.
            self.global_updating_rule()

    def iteration(self):
        self.avg_path_cost = 0
        self.ant_counter = 0
        self.iter_counter += 1
        for ant in self.ants:
            ant.run()

    def num_ants(self):
        return len(self.ants)

    def num_iterations(self):
        return self.num_iterations

    def iteration_counter(self):
        return self.iter_counter

    def update(self, ant):
        print "Update called by %s" % (ant.ID,)
        self.ant_counter += 1
        self.avg_path_cost += ant.path_cost
        if ant.path_cost < self.bpc:
            self.bpc = ant.path_cost
            self.bpm = ant.path_mat
            self.bpv = ant.path_vec
            self.lbpi = self.iter_counter
        if self.ant_counter == len(self.ants):
            self.avg_path_cost /= len(self.ants)
            print "Best: %s, %s, %s, %s" % (
                self.bpv, self.bpc, self.iter_counter, self.avg_path_cost,)


    def done(self):
        return self.iter_counter == self.num_iterations

    def c_workers(self):
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
        for r in range(0, self.graph.num_nodes):
            for s in range(0, self.graph.num_nodes):
                if r != s:
                    delt_tau = self.bpm[r][s] / self.bpc # This is 0 if r->s is not on current best path
                    evaporation = (1 - self.Alpha) * self.graph.tau(r, s) # 10% of pheromone evaporates
                    deposition = self.Alpha * delt_tau # deposition inversely proportional to total path length
                    self.graph.update_tau(r, s, evaporation + deposition)

class GraphBit:
    def __init__(self, num_nodes, delta_mat, tau_mat=None):
        print len(delta_mat)
        if len(delta_mat) != num_nodes:
            raise Exception("len(delta) != num_nodes")
        self.num_nodes = num_nodes
        self.delta_mat = delta_mat # distance matrix
        if tau_mat is None:
            self.tau_mat = []  # init as matrix of 0s with a row and column for each city
            for i in range(0, num_nodes):
                self.tau_mat.append([0] * num_nodes)

    # Distance between cities r and s
    def delta(self, r, s):
        return self.delta_mat[r][s]

    # Amount of pheromone between cities r and s
    def tau(self, r, s):
        return self.tau_mat[r][s]

    def etha(self, r, s):
        return 1.0 / self.delta(r, s)

    def update_tau(self, r, s, val):
        self.tau_mat[r][s] = val

    # Init amount of pheromone between all cities to be the same
    # The amount is inversely proportional to the number of cities
    # and the average distance between cities.
    def reset_tau(self):
        avg = self.average_delta()
        self.tau0 = 1.0 / (self.num_nodes * 0.5 * avg)
        print "Average = %s" % (avg,)
        print "Tau0 = %s" % (self.tau0)
        for r in range(0, self.num_nodes):
            for s in range(0, self.num_nodes):
                self.tau_mat[r][s] = self.tau0


    # Average distance between cities
    def average_delta(self):
        return self.average(self.delta_mat)


    def average_tau(self):
        return self.average(self.tau_mat)

    def average(self, matrix):
        sum = 0
        for r in range(0, self.num_nodes):
            for s in range(0, self.num_nodes):
                sum += matrix[r][s]

        avg = sum / (self.num_nodes * self.num_nodes)
        return avg

import pickle
import sys
import traceback


def main(argv):
    nm = 10

    if len(argv) >= 3 and argv[0]:
        nm = int(argv[0])

    if nm <= 10: # number of cities to visit
        na = 20 # number of ants
        ni = 12 # number of iterations
        nr = 1 # number of repetitions of the entire algorithm
    else:
        na = 28
        ni = 20
        nr = 1

    stuff = pickle.load(open(argv[1], "r"))
    cities = stuff[0]
    cm = stuff[1] # distances for each city
    #why are we doing this?
    if nm < len(cm):
        # cut off the distances we're not going to use
        # in both dimensions (remove cities from top level
        # and from each city's array)
        cm = cm[0:nm]
        for i in range(0, nm):
            cm[i] = cm[i][0:nm]



    try:
        graph = GraphBit(nm, cm)
        bpv = None
        bpc = sys.maxint
        for i in range(0, nr):
            print "Repetition %s" % i
            graph.reset_tau() # Reset pheromone to equally distributed
            workers = BigGroup(graph, na, ni)
            print "Colony Started"
            workers.start()
            if workers.bpc < bpc:
                print "Colony Path"
                bpv = workers.bpv
                bpc = workers.bpc

        print "\n------------------------------------------------------------"
        print "                     Results                                "
        print "------------------------------------------------------------"
        print "\nBest path = %s" % (bpv,)
        city_vec = []
        for node in bpv:
            print cities[node] + " ",
            city_vec.append(cities[node])
        print "\nBest path cost = %s\n" % (bpc,)
        results = [bpv, city_vec, bpc]
        pickle.dump(results, open(argv[2], 'w+'))
    except Exception, e:
        print "exception: " + str(e)
        traceback.print_exc()


if __name__ == "__main__":
    main(sys.argv[1:])
