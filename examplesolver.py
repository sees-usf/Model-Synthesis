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
    list = [];

    # Creates the variables.
    num_vals = 3
    x10 = model.NewIntVar(60, 60, 'x10')
    x15 = model.NewIntVar(20, 20, 'x15')
    x17 = model.NewIntVar(40, 40, 'x17')
    x19 = model.NewIntVar(40, 40, 'x19')
    x23 = model.NewIntVar(20, 20, 'x23')
    x27 = model.NewIntVar(60, 60, 'x27')
    x38 = model.NewIntVar(30, 30, 'x38')
    x39 = model.NewIntVar(30, 30, 'x39')
    x40 = model.NewIntVar(30, 30, 'x40')
    x41 = model.NewIntVar(30, 30, 'x41')
    
    x1017 = model.NewIntVar(0, 40, 'x1017')
    list.append(x1017)

    x1027 = model.NewIntVar(0, 60, 'x1027')
    list.append(x1027)

    x1523 = model.NewIntVar(0, 20, 'x1523')
    list.append(x1523)

    x1719 = model.NewIntVar(0, 40, 'x1719')
    list.append(x1719)

    x1917 = model.NewIntVar(0, 37, 'x1917')
    x1927 = model.NewIntVar(0, 40, 'x1927')
    list.append(x1917)
    list.append(x1927)

    x2310 = model.NewIntVar(0, 18, 'x2310')
    x2315 = model.NewIntVar(0, 18, 'x2315')
    x2340 = model.NewIntVar(0, 17, 'x2340')
    x2341 = model.NewIntVar(0, 18, 'x2341')
    list.append(x2310)
    list.append(x2315)
    list.append(x2340)
    list.append(x2341)
    
    x2710 = model.NewIntVar(0, 55, 'x2710')
    x2715 = model.NewIntVar(0, 20, 'x2715')
    x2740 = model.NewIntVar(0, 30, 'x2740')
    x2741 = model.NewIntVar(0, 30, 'x2741')
    list.append(x2710)
    list.append(x2715)
    list.append(x2740)
    list.append(x2741)

    x3810 = model.NewIntVar(0, 30, 'x3810')
    x3815 = model.NewIntVar(0, 20, 'x3815')
    x3840 = model.NewIntVar(0, 30, 'x3840')
    x3841 = model.NewIntVar(0, 30, 'x3841')
    list.append(x3810)
    list.append(x3815)
    list.append(x3840)
    list.append(x3841)
    
    x3910 = model.NewIntVar(0, 30, 'x3910')
    x3915 = model.NewIntVar(0, 20, 'x3915')
    x3940 = model.NewIntVar(0, 29, 'x3940')
    x3941 = model.NewIntVar(0, 30, 'x3941')
    list.append(x3910)
    list.append(x3915)
    list.append(x3940)
    list.append(x3941)
    

    # Creates the constraints.
    
    model.Add(x10 == (x1017 + x1027))
    model.Add(x10 == (x2310 + x2710 + x3810 + x3910))

    model.Add(x15 == x1523)
    model.Add(x15 == (x2315 + x2715 + x3815 + x3915))

    model.Add(x17 == x1719)
    model.Add(x17 == (x1017 + x1917))

    model.Add(x19 == (x1917 + x1927))
    model.Add(x19 == x1719)

    model.Add(x23 == (x2310 + x2315 + x2340 + x2341))
    model.Add(x23 == x1523)

    model.Add(x27 == (x2710 + x2715 + x2740 + x2741))
    model.Add(x27 == (x1027 + x1927))

    model.Add(x38 == (x3810 + x3815 + x3840 + x3841))

    model.Add(x39 == (x3910 + x3915 + x3940 + x3941))


    model.Add(x40 == (x2340 + x2740 + x3840 + x3940))

    model.Add(x41 == (x2341 + x2741 + x3841 + x3941))

    
    # Create a solver and solve.
    solver = cp_model.CpSolver()
    solution_printer = VarArraySolutionPrinter(list)
    status = solver.SearchForAllSolutions(model, solution_printer)

    print('Status = %s' % solver.StatusName(status))
    print('Number of solutions found: %i' % solution_printer.solution_count())
    
SearchForAllSolutionsSampleSat()
