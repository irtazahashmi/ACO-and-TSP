import os, sys
from typing import Dict

from src.Route import Route

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import traceback
from src.Coordinate import Coordinate
from src.Direction import Direction
from src.SurroundingPheromone import SurroundingPheromone


# Class that holds all the maze data. This means the pheromones, the open and blocked tiles in the system as
# well as the starting and end coordinates.
class Maze:

    # Constructor of a maze
    # @param walls int array of tiles accessible (1) and non-accessible (0)
    # @param width width of Maze (horizontal)
    # @param length length of Maze (vertical)
    def __init__(self, walls, width, length):
        self.walls = walls
        self.length = length
        self.width = width
        self.start = None
        self.end = None
        self.maze_pheromones: Dict[(int, int), float] = dict()
        self.initialize_pheromones()

    # Initialize pheromones to a start value.
    def initialize_pheromones(self):
        self.maze_pheromones = dict()

        for x in range(0, self.width):
            for y in range(0, self.length):
                if self.walls[x][y] == 1:
                    self.maze_pheromones[(x, y)] = 1

    # Reset the maze for a new shortest path problem.
    def reset(self):
        self.initialize_pheromones()

    def remove_pheromone(self, cord: Coordinate, mod=0.5):
        self.maze_pheromones[(cord.get_x(), cord.get_y())] = self.maze_pheromones[(cord.get_x(), cord.get_y())] * mod

    # Update the pheromones along a certain route according to a certain Q
    # @param r The route of the ants
    # @param Q Normalization factor for amount of dropped pheromone
    def add_pheromone_route(self, route, q):
        deltaTau = q / route.size()

        start = route.get_start()
        cur: Coordinate = start
        seen = []
        for d in route.get_route():
            if cur not in seen:
                curTau = self.get_pheromone(cur)
                self.maze_pheromones[(cur.get_x(), cur.get_y())] = curTau + deltaTau
                seen.append(cur)

            cur = cur.add_direction(d)

    # Update pheromones for a list of routes
    # @param routes A list of routes
    # @param Q Normalization factor for amount of dropped pheromone
    def add_pheromone_routes(self, routes, q):
        r: Route
        for r in routes:
            if r.done:
                self.add_pheromone_route(r, q)

    # Evaporate pheromone
    # @param rho evaporation factor
    def evaporate(self, rho):
        for key, value in self.maze_pheromones.items():
            self.maze_pheromones[key] = (1 - rho) * value

    # Width getter
    # @return width of the maze
    def get_width(self):
        return self.width

    # Length getter
    # @return length of the maze
    def get_length(self):
        return self.length

    # Returns a the amount of pheromones on the neighbouring positions (N/S/E/W).
    # @param position The position to check the neighbours of.
    # @return the pheromones of the neighbouring positions.
    def get_surrounding_pheromone(self, position: Coordinate) -> SurroundingPheromone:
        n = self.get_pheromone_check(position.add_direction(Direction.north))
        e = self.get_pheromone_check(position.add_direction(Direction.east))
        s = self.get_pheromone_check(position.add_direction(Direction.south))
        w = self.get_pheromone_check(position.add_direction(Direction.west))

        return SurroundingPheromone(n, e, s, w)

    def get_pheromone_check(self, pos):
        if (pos.get_x(), pos.get_y()) in self.maze_pheromones:
            return self.get_pheromone(pos)
        else:
            return 0

    # Pheromone getter for a specific position. If the position is not in bounds returns 0
    # @param pos Position coordinate
    # @return pheromone at point
    def get_pheromone(self, pos):
        return self.maze_pheromones[(pos.get_x(), pos.get_y())]

    # Check whether a coordinate lies in the current maze.
    # @param position The position to be checked
    # @return Whether the position is in the current maze
    def in_bounds(self, position):
        return position.x_between(0, self.width) and position.y_between(0, self.length)

    # Representation of Maze as defined by the input file format.
    # @return String representation
    def __str__(self):
        string = ""
        string += str(self.width)
        string += " "
        string += str(self.length)
        string += " \n"
        for y in range(self.length):
            for x in range(self.width):
                string += str(self.walls[x][y])
                string += " "
            string += "\n"
        return string

    # Method that builds a mze from a file
    # @param filePath Path to the file
    # @return A maze object with pheromones initialized to 0's inaccessible and 1's accessible.
    @staticmethod
    def create_maze(file_path):
        try:
            f = open(file_path, "r")
            lines = f.read().splitlines()
            dimensions = lines[0].split(" ")
            width = int(dimensions[0])
            length = int(dimensions[1])

            # make the maze_layout
            maze_layout = []
            for x in range(width):
                maze_layout.append([])

            for y in range(length):
                line = lines[y + 1].split(" ")
                for x in range(width):
                    if line[x] != "":
                        state = int(line[x])
                        maze_layout[x].append(state)
            print("Ready reading maze file " + file_path)
            return Maze(maze_layout, width, length)
        except FileNotFoundError:
            print("Error reading maze file " + file_path)
            traceback.print_exc()
            sys.exit()

    def write_to_file(self, file_path, b):
        f = open(file_path, "w")
        string = ""

        for x in range(0, self.length):
            for y in range(0, self.width):
                c = Coordinate(y, x)
                o = self.get_pheromone_check(c)
                if c.__str__() in b:
                    o = 0
                string += str(o) + "\t"
            string += "\n"

        f.write(string)
