from plantuml import *


class SolutionGenerator:
    def __init__(self, solutions, directory_name, graph):
        self.solutions = solutions
        self.directory_name = directory_name
        self.graph = graph
        self.plantuml = PlantUML()
        self.sequences = []




