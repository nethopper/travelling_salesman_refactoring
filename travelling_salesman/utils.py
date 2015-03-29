def cut_to_size(matrix, size):
    """Cut off the distances we're not going to use in both dimensions (remove nodes from top level and from each city's array)"""
    if size >= len(matrix):
        return matrix

    matrix = matrix[0:size]
    for i in range(size):
        matrix[i] = matrix[i][0:size]
    return matrix

def create_matrix(size, value):
    return [[value for x in range(size)] for y in range(size)]

def empty_matrix(size):
    create_matrix(size, 0)
