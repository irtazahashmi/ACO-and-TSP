import operator
import os, sys
from math import sqrt

ITERATIONS = 60000

ALPHA = 1
BETA = 0.2
DEBUG = False

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import random
from src.Route import Route
from src.Coordinate import Coordinate
from src.Direction import Direction
from src.SurroundingPheromone import SurroundingPheromone


# Class that represents the ants functionality.
class Ant:
    current_position: Coordinate = None

    # Constructor for ant taking a Maze and PathSpecification.
    # @param maze Maze the ant will be running in.
    # @param spec The path specification consisting of a start coordinate and an end coordinate.
    def __init__(self, maze, path_specification):
        self.blocked = dict()
        self.maze = maze
        self.start: Coordinate = path_specification.get_start()
        self.end: Coordinate = path_specification.get_end()
        self.current_position: Coordinate = self.start
        self.rand = random

    # Method that performs a single run through the maze by the ant.
    # @return The route the ant found through the maze.
    def find_route(self):
        route = Route(self.start)
        not_dir = None
        prev_pos = self.start
        seen = dict({self.current_position.__str__(): 1})
        visited = dict({self.current_position.__str__(): 1})

        for r in range(0, ITERATIONS):
            if self.current_position == self.end:
                route.done = True
                if DEBUG:
                    self.maze.write_to_file("./../data/maze.csv", self.blocked)
                break
            if r >= ITERATIONS - 1:
                if DEBUG:
                    self.maze.write_to_file("./../data/maze.csv", self.blocked)
                print("ran out")
            s_pheromones: SurroundingPheromone = self.maze.get_surrounding_pheromone(self.current_position)
            total = 0
            #  calc Pheromone on all paths departing from cur loc i
            for j in Direction:
                dir_cord = self.current_position.add_direction(j)
                if dir_cord == prev_pos or j == not_dir or dir_cord.__str__() in self.blocked:
                    continue
                mod = 1
                if dir_cord.__str__() in seen:
                    mod = 0.1
                total += self.calc_pheromone(j, s_pheromones) * mod

            prob_map_for_possible_dirs = dict()
            if total != 0:
                # calc prob
                for i in Direction:
                    c = self.current_position.add_direction(i)
                    if c == prev_pos or i == not_dir or c.__str__() in self.blocked:
                        continue
                    mod = 1
                    if c.__str__() in seen:
                        mod = 0.1

                    p = self.calc_pheromone(i, s_pheromones) * mod / total
                    prob_map_for_possible_dirs[i] = p

                # get random dir based on the probability
                direction = self.rand.choices(
                    list(prob_map_for_possible_dirs.keys()),
                    weights=list(prob_map_for_possible_dirs.values()),
                    k=1).pop()

                route.add(direction)
                prev_pos = self.current_position
                self.current_position = self.current_position.add_direction(direction)

                if not_dir is not None:
                    not_dir = None

                # remove loop
                if self.current_position.__str__() in visited:
                    if DEBUG:
                        print("loop: ", end=" ")
                        print("(" + self.current_position.__str__() + "): " + str(self.num_of_dirs()), end=", ")

                    # go back one step
                    go_to_c = self.current_position
                    not_dir = route.remove_last()
                    self.current_position = self.current_position.subtract_direction(not_dir)

                    # block all that only have 2 directions
                    if self.num_of_dirs() <= 2:
                        self.blocked[self.current_position.__str__()] = 1
                    visited.popitem()

                    # go back to start of loop
                    while self.current_position != go_to_c:
                        if DEBUG:
                            print("(" + self.current_position.__str__() + "): " + str(self.num_of_dirs()), end=", ")
                        not_dir = route.remove_last()
                        self.current_position = self.current_position.subtract_direction(not_dir)
                        visited.popitem()

                    if DEBUG:
                        print("")
                    # reset last position
                    prev_pos = self.get_prev_pos(route, visited)
                    if DEBUG:
                        self.maze.write_to_file("./../data/maze.csv", self.blocked)

                visited[self.current_position.__str__()] = 1
                seen[self.current_position.__str__()] = 1
            else:
                if DEBUG:
                    print("block: ", end=" ")
                    print("(" + self.current_position.__str__() + "): " + str(self.num_of_dirs()), end=", ")

                # backtrack
                not_dir, prev_pos = self.backtrack(route, visited)
                if DEBUG:
                    print("")
        route.end = self.end
        return route

    def get_prev_pos(self, route, visited):
        if len(visited) > 1:
            last = route.remove_last()
            prev_pos = self.current_position.subtract_direction(last)
            route.add(last)
        else:
            prev_pos = self.start
        return prev_pos

    def backtrack(self, route, visited):
        not_dir = None
        while self.num_of_dirs() < 2 and not (self.current_position == self.start):
            not_dir = route.remove_last()
            self.blocked[self.current_position.__str__()] = 1
            self.current_position = self.current_position.subtract_direction(not_dir)  # move back
            visited.popitem()
            if DEBUG:
                print("(" + self.current_position.__str__() + "): " + str(self.num_of_dirs()), end=", ")

        prev_pos = self.get_prev_pos(route, visited)
        return not_dir, prev_pos

    def num_of_dirs(self):
        ret = 0
        for d in Direction:
            c = self.current_position.add_direction(d)
            if self.maze.get_pheromone_check(c) > 0 and c.__str__() not in self.blocked:
                ret += 1
        return ret

    def calc_pheromone(self, i, s_pheromones):
        euclid = self.euclid_to_goal(i)
        return (s_pheromones.get(i) ** ALPHA) * (euclid ** BETA)

    def euclid_to_goal(self, direction):
        x, y = self.get_x_y_to_goal(direction)
        return x ** 2 + y ** 2 if x ** 2 + y ** 2 != 0 else 1

    def get_x_y_to_goal(self, i):
        x = self.end.get_x() - self.current_position.add_direction(i).get_x()
        y = self.end.get_y() - self.current_position.add_direction(i).get_y()
        return x, y
