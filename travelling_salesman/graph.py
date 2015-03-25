import logging

class Graph:
    def __init__(self, num_nodes, distance_matrix, pheromone_mat=None):
        logging.debug(len(distance_matrix))
        if len(distance_matrix) != num_nodes:
            raise Exception("len(distance) != num_nodes")
        self.num_nodes = num_nodes
        self.distance_matrix = distance_matrix
        if pheromone_mat is None:
            self.pheromone_mat = self.empty_pheromone_matrix()

    def empty_pheromone_matrix(self):
        """Return a zero matrix with a row and column for each city"""
        pheromone_matrix = []
        for i in range(0, self.num_nodes):
            pheromone_matrix.append([0] * self.num_nodes)
        return pheromone_matrix


    def distance(self, r, s):
        """Distance between cities r and s"""
        return self.distance_matrix[r][s]

    def pheromone(self, r, s):
        """Amount of pheromone between cities r and s"""
        return self.pheromone_mat[r][s]

    def inverse_distance(self, r, s):
        """Inverse of distance between cities r and s"""
        return 1.0 / self.distance(r, s)

    def update_pheromone(self, r, s, val):
        """Set amount pheromone on edge between r and s to be val"""
        self.pheromone_mat[r][s] = val


    def reset_pheromone(self):
        """Reset amount of pheromone between all cities to be the same. The amount is inversely proportional to the number of cities and the average distance between cities."""
        avg = self.average_distance()
        self.pheromone0 = 1.0 / (self.num_nodes * 0.5 * avg)
        logging.debug("Average = %s", avg)
        logging.debug("pheromone0 = %s", self.pheromone0)
        self.pheromone_mat = [[self.pheromone0] * self.num_nodes for i in range(self.num_nodes)]

    # Average distance between cities
    def average_distance(self):
        return self.average(self.distance_matrix)


    def average_pheromone(self):
        return self.average(self.pheromone_mat)

    def average(self, matrix):
        return sum([sum(row) for row in matrix]) / (self.num_nodes * self.num_nodes)
