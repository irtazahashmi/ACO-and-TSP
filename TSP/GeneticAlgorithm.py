import os, sys, numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import random
from src.TSPData import TSPData

# TSP problem solver using genetic algorithms.
class GeneticAlgorithm:

    # Constructs a new 'genetic algorithm' object.
    # @param generations the amount of generations.
    # @param popSize the population size.
    def __init__(self, generations, pop_size):
        self.generations = generations
        self.pop_size = pop_size

     # Knuth-Yates shuffle, reordering an array randomly
     # @param chromosome array to shuffle.
    def shuffle(self, chromosome):
        n = len(chromosome)
        for i in range(n):
            r = i + int(random.uniform(0, 1) * (n - i))
            swap = chromosome[r]
            chromosome[r] = chromosome[i]
            chromosome[i] = swap
        return chromosome

    # Fitness function
    def fitness_function(self, distance, distances):
        fitness = sys.maxsize
        for dist in distances:
            if dist < distance and dist != distance:
                fitness = dist
        return fitness

    # Crossover
    def crossover(self, crossover_pt, pair_cs):
        if pair_cs[0] < pair_cs[1]:
            shift = crossover_pt * pair_cs[1]
            pair_cs[1] -= shift
            pair_cs[0] += shift
        else:
            shift = crossover_pt * pair_cs[0]
            pair_cs[0] -= shift
            pair_cs[1] += shift
        return pair_cs

    # Mutation
    def mutation(self, chromosome):
        bit_str = bin(chromosome)

        if bit_str[len(bit_str) - 1] == '0':
            bit_str[len(bit_str) - 1] = '1'
        else:
            bit_str[len(bit_str) - 1] = '0'

        mut_cs = int (bit_str, 2)
        return mut_cs

    # This method should solve the TSP.
    # @param pd the TSP data.
    # @return the optimized product sequence.
    def solve_tsp(self, tsp_data: TSPData):
        # list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17]

        # Get the list of distances
        # [ [ {0,0}.size  {0,1}.size  ... ] , [  {1,0}.size  ... ],   ...]
        distances = tsp_data.get_distances()

        # Pick the initial sample of chromosomes
        chromosomes = []

        random_indices = [random.randint(0, len(distances) - 1) for _ in range(18)]
        for random_index in random_indices:
            random_ind = random.randint(0, len(distances[random_index]) - 1)
            chromosomes.append(distances[random_index][random_ind])

        # Shuffle them randomly
        self.shuffle(chromosomes)

        # Find fitness for each chromosome
        fitness_cs = []
        for chromosome in chromosomes:
            fitness_c = self.fitness_function(chromosome, chromosomes)
            fitness_cs.append(fitness_c)

        # Find fitness ratios
        fitness_ratios = []
        sum_fitness_cs = np.sum(fitness_cs)
        for fitness_c in fitness_cs:
            fitness_ratios.append(fitness_c / sum_fitness_cs * 100)

        # Cumulative fitness ratio
        cumulative_fitness = []
        for i in range(0, len(fitness_ratios) - 1):
            cumulative_fitness.append(fitness_ratios[i] + np.sum(fitness_ratios[0:i]))

        # Roulette wheel selection
        pair_cs = []
        random_nos = [random.randint(0, np.argmax(cumulative_fitness)) for _ in range(2)]
        for i in range(0, len(cumulative_fitness)):
            count = 0
            if i != len(cumulative_fitness) and count < 2:
                if np.abs(cumulative_fitness[i] - cumulative_fitness[i + 1]) < random_nos[i]:
                    pair_cs.append(chromosomes[i])
                    count += 1

        # Crossover
        pc = 0.7
        crossover_pt = random.randint(0, 100) / 100
        if crossover_pt < pc:
            new_pair_cs = self.crossover(crossover_pt, pair_cs)
        else:
            new_pair_cs = pair_cs

        # Update chromosomes
        for parent in pair_cs:
            chromosomes.remove(parent)
        for new_parent in new_pair_cs:
            chromosomes.append(new_parent)

        # Mutation
        pm = 0.01
        rand = random.randint(0, 100) / 100
        for chromosome in chromosomes:
            if rand <= pm:
                chromosomes.remove(chromosome)
                chromosomes.append(self.mutation(chromosome))

        return chromosomes

# Assignment 2.b
if __name__ == "__main__":
    #parameters
    population_size = 20
    generations = 20
    persistFile = "./../tmp/productMatrixDist"

    # setup optimization
    tsp_data = TSPData.read_from_file(persistFile)
    ga = GeneticAlgorithm(generations, population_size)

    # run optimzation and write to file
    solution = ga.solve_tsp(tsp_data)
    tsp_data.write_action_file(solution, "./../data/easy_solution.txt")

    distances = tsp_data.get_distances()