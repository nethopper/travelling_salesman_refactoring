import logging

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
