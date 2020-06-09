from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from py4j.java_gateway import JavaGateway

from ortools.sat.python import cp_model

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0

    def on_solution_callback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s=%i' % (v, self.Value(v)), end=' ')
        print()

    def solution_count(self):
        return self.__solution_count


def SearchForAllSolutionsSampleSat():
    """Minimal CP-SAT example to showcase calling the solver."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    num_vals = 3
    x1 = model.NewIntVar(2, 2, 'x1')
    x2 = model.NewIntVar(2, 2, 'x2')
    x3 = model.NewIntVar(2, 2, 'x3')
    x4 = model.NewIntVar(2, 2, 'x4')
    x5 = model.NewIntVar(2, 2, 'x5')
    x6 = model.NewIntVar(2, 2, 'x6')
    x12 = model.NewIntVar(0, 2, 'x12')
    x14 = model.NewIntVar(0, 2, 'x14')
    x15 = model.NewIntVar(0, 2, 'x15')
    x32 = model.NewIntVar(0, 2, 'x32')
    x34 = model.NewIntVar(0, 2, 'x34')
    x35 = model.NewIntVar(0, 1, 'x35')
    x56 = model.NewIntVar(0, 2, 'x56')
    x62 = model.NewIntVar(0, 2, 'x62')
    x64 = model.NewIntVar(0, 2, 'x64')

    # Creates the constraints.
    
    model.Add(x1 == (x12 + x14 + x15))
    model.Add(x3 == (x32 + x34 + x35))
    model.Add((x15 + x35) == x5)
    model.Add(x5 == x56)
    model.Add(x6 == (x62 + x64))
    model.Add(x2 == (x12 + x32 + x62))
    model.Add(x4 == (x64 + x34 + x14))
    
    """
    model.Add(x34 < 2)
    model.Add(x32 < 2)
    model.Add(x15 < 2)
    model.Add(x62 < 2)
    model.Add(x64 < 2)
    
    """
    
    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([x12, x14, x15, x32, x34, x35, x56, x62, x64])
    status = solver.SearchForAllSolutions(model, solution_printer)

    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_printer.solution_count())
    
SearchForAllSolutionsSampleSat()
