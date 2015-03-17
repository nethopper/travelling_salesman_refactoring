import logging
import sys
import random
from ant import Ant

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

