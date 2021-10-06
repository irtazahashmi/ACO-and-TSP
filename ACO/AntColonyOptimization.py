import os, sys
import multiprocessing
from multiprocessing.queues import SimpleQueue
from typing import Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import time
from src.Maze import Maze
from src.PathSpecification import PathSpecification
from src.Ant import Ant

THREADING = True


# Class representing the first assignment. Finds shortest path between two points in a maze according to a specific
# path specification.
class AntColonyOptimization:

    # Constructs a new optimization object using ants.
    # @param maze the maze .
    # @param antsPerGen the amount of ants per generation.
    # @param generations the amount of generations.
    # @param Q normalization factor for the amount of dropped pheromone
    # @param evaporation the evaporation factor.
    def __init__(self, maze, ants_per_gen, generations, q, evaporation):
        self.maze = maze
        self.ants_per_gen = ants_per_gen
        self.generations = generations
        self.q = q
        self.evaporation = evaporation
        self.routes = []

    # Loop that starts the shortest path process
    # @param spec Spefication of the route we wish to optimize
    # @return ACO optimized route
    def find_shortest_route(self, path_specification, q=None):
        self.maze.reset()
        # start_pt = path_specification.get_start(path_specification)
        # end_pt = path_specification.get_end(path_specification)
        route = None
        for gen in range(0, self.generations):
            self.routes = []
            threads = []
            if THREADING:
                queue: SimpleQueue[Any] = multiprocessing.SimpleQueue()
            for ant_i in range(0, self.ants_per_gen):
                if THREADING:
                    t = multiprocessing.Process(target=self.run, args=(path_specification, queue))
                    t.start()
                    threads.append(t)
                else:
                    self.run(path_specification)
                    print("gen: " + str(gen) + ", ant: " + str(ant_i) + ", len " + str(len(self.routes[-0].get_route())))

            if THREADING:
                for t in threads:
                    self.routes.append(queue.get())
            # TSPData includes paths from C to C return early with 0 path
            if path_specification.start == path_specification.end:
                if THREADING:
                    q.put(self.routes.pop())
                    return
                else:
                    return self.routes.pop()

            self.maze.evaporate(self.evaporation)
            self.maze.add_pheromone_routes(self.routes, self.q)
            s = 100000
            l = 0
            a = 0
            route = self.routes[0]
            c = 0
            for r in self.routes:
                if not r.done:
                    continue
                c += 1
                if r.size() > l: l = r.size()
                if r.size() < s: s = r.size()
                a += r.size()
                if r.shorter_than(route):
                    route = r
            print("gen: " + str(gen) + ", shortest: " + str(s) + ", avg: " + str(
                a / c) + ", longest: " + str(l))

        if q is not None:
            q.put(route)
        else:
            return route

    def run(self, path_specification, qeueu=None):
        ant = Ant(self.maze, path_specification)
        route = ant.find_route()
        if THREADING:
            qeueu.put(route)
        else:
            self.routes.append(route)


# Driver function for Assignment 1
if __name__ == "__main__":
    # parameters
    gen = 25
    no_gen = 10
    q = 1000
    evap = 0.5

    # construct the optimization objects
    maze = Maze.create_maze("./../data/hard maze.txt")
    spec = PathSpecification.read_coordinates("./../data/hard coordinates.txt")
    aco = AntColonyOptimization(maze, gen, no_gen, q, evap)

    # save starting time
    start_time = int(round(time.time() * 1000))

    # run optimization
    shortest_route = aco.find_shortest_route(spec)

    # print time taken
    print("Time taken: " + str((int(round(time.time() * 1000)) - start_time) / 1000.0))

    # save solution
    shortest_route.write_to_file("./../data/hard_solution.txt")

    # print route size
    print("Route size: " + str(shortest_route.size()))

    # Print routes
    # print(shortest_route)
