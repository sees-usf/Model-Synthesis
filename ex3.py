from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
    x38 = model.NewIntVar(30, 30, 'x38')
    x10 = model.NewIntVar(60, 60, 'x10')
    x39 = model.NewIntVar(30, 30, 'x39')
    x17 = model.NewIntVar(40, 40, 'x17')
    x19 = model.NewIntVar(40, 40, 'x19')
    x27 = model.NewIntVar(60, 60, 'x27')
    x15 = model.NewIntVar(20, 20, 'x15')
    x23 = model.NewIntVar(20, 20, 'x23')
    x40 = model.NewIntVar(30, 30, 'x40')
    x41 = model.NewIntVar(30, 30, 'x41')

    x38_10 = model.NewIntVar(0, 30, 'x38_10')
    x38_15 = model.NewIntVar(0, 20, 'x38_15')
    x38_40 = model.NewIntVar(0, 30, 'x38_40')
    x38_41 = model.NewIntVar(0, 30, 'x38_41')
    x39_10 = model.NewIntVar(0, 30, 'x39_10')
    x39_15 = model.NewIntVar(0, 20, 'x39_15')
    x39_40 = model.NewIntVar(0, 29, 'x39_40')
    x39_41 = model.NewIntVar(0, 30, 'x39_41')
    x10_17 = model.NewIntVar(0, 40, 'x10_17')
    x10_27 = model.NewIntVar(0, 60, 'x10_27')
    x17_19 = model.NewIntVar(0, 40, 'x17_19')
    #x19_17 = model.NewIntVar(0, 37, 'x19_17')
    x19_27 = model.NewIntVar(0, 40, 'x19_27')
    #x27_10 = model.NewIntVar(0, 55, 'x27_10')
    x27_15 = model.NewIntVar(0, 20, 'x27_15')
    x27_40 = model.NewIntVar(0, 30, 'x27_40')
    x27_41 = model.NewIntVar(0, 30, 'x27_41')
    x15_23 = model.NewIntVar(0, 20, 'x15_23')
    #x23_10 = model.NewIntVar(0, 18, 'x23_10')
    #x23_15 = model.NewIntVar(0, 18, 'x23_15')
    x23_40 = model.NewIntVar(0, 17, 'x23_40')
    x23_41 = model.NewIntVar(0, 18, 'x23_41')


    # Creates the constraints.
    model.Add(x38 == (x38_10 + x38_15 + x38_40 + x38_41))
    model.Add(x39 == (x39_10 + x39_15 + x39_40 + x39_41))
    model.Add(x10 == (x10_17 + x10_27))
    model.Add((x38_10 + x39_10) == x10)
    model.Add(x17 == x17_19)
    model.Add((x10_17) == x17)
    model.Add(x19 == (x19_27))
    model.Add(x17_19 == x19)
    model.Add(x27 == (x27_15 + x27_40 + x27_41))
    model.Add((x10_27 + x19_27) == x27)
    model.Add(x15 == x15_23)
    model.Add((x38_15 + x39_15 + x27_15) == x15)
    model.Add(x23 == (x23_40 + x23_41))
    model.Add((x15_23) == x23)
    model.Add((x23_40 + x27_40 + x38_40 + x39_40) == x40)
    model.Add((x23_41 + x27_41 + x38_41 + x39_41) == x41)

    
##    solver = cp_model.CpSolver()
##    status = solver.Solve(model)
##
##    if status == cp_model.FEASIBLE:
##        print('feasiable soultion')
##
##    else:
##        print('no feasiable soultion')
        
    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter([
                x38_10, 
                x38_15,
                x38_40,
                x38_41,
                x39_10,
                x39_15,
                x39_40,
                x39_41,
                x10_17,
                x10_27,
                x17_19,
                #x19_17,
                x19_27,
                #x27_10,
                x27_15,
                x27_40,
                x27_41,
                x15_23,
                #x23_10,
                #x23_15,
                x23_40,
                x23_41])
    status = solver.SearchForAllSolutions(model, solution_printer)

    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_printer.solution_count())
    
SearchForAllSolutionsSampleSat()
