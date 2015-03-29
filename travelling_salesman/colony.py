import logging
import sys
import random
import graph as g
import ant as a


class Colony:
    def __init__(self, graph, num_ants, num_iterations, params):
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.Alpha = params['alpha']
        self.reset()
        self.params = params

    def reset(self):
        self.best_path_cost = sys.maxint
        self.best_path = None
        self.best_path_matrix = None
        self.best_path_iteration = 0

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
            self.update(a.run(ant))


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
            self.update_best_path(ant)
        if self.ant_counter == len(self.ants):
            self.avg_path_cost /= len(self.ants)
            logging.debug("Best: %s, %s, %s, %s",
                          self.best_path, self.best_path_cost, self.iteration, self.avg_path_cost)

    def update_best_path(self, ant):
        self.best_path_cost = ant['path_cost']
        self.best_path_matrix = ant['path_matrix']
        self.best_path = ant['path']
        self.best_path_iteration = self.iteration

    def done(self):
        return self.iteration == self.num_iterations

    def create_workers(self):
        ants = []
        ant_params =  dict((param, self.params[param]) for param in a.required_params)
        for i in range(0, self.num_ants):
            ant = a.create_ant(i, random.randint(0, g.size(self.graph) - 1),
                               self.graph, ant_params)
            ants.append(ant)

        return ants

    def global_updating_rule(self):
        node_list = range(g.size(self.graph))
        [self.update_pheromone_between(start, end)
         for start in node_list
         for end in node_list
         if start != end]

    def update_pheromone_between(self, start, end):
        """Update amount of pheromone between start and end by calculating evaporation and deposition. A constant (Alpha) percentage evaporates. Deposition is inversely proportional to total path length, but 0 if this is not one the best paths found."""
        delt_pheromone = self.best_path_matrix[start][end] / self.best_path_cost
        evaporation = (1 - self.Alpha) * self.graph['pheromones'][start][end]
        deposition = self.Alpha * delt_pheromone
        self.graph['pheromones'][start][end] = evaporation + deposition
