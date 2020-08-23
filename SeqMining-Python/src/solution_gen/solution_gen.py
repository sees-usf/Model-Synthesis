from plantuml import *


class SolutionGenerator:
    def __init__(self, solutions, directory_name, graph):
        self.solutions = solutions
        self.directory_name = directory_name
        self.graph = graph
        self.plantuml = PlantUML()
        self.sequences = []

    def generate_solutions(self):
        self.extract_sequences()
        self.generate_plantuml_pngs()
        self.generate_solution_file()

    def extract_sequences(self):
        pass

    def generate_plantuml_pngs(self):
        pass

    def generate_solution_file(self):
        pass
    
    

