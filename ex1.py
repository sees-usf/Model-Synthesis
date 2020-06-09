from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.sat.python import cp_model


def SimpleSatProgram():
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
    
    model.Add(x34 < 2)
    model.Add(x32 < 2)
    model.Add(x15 < 2)
    model.Add(x62 < 2)
    model.Add(x64 < 2)
    
    

    # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE:
        print('x12 = %i' % solver.Value(x12))
        print('x14 = %i' % solver.Value(x14))
        print('x15 = %i' % solver.Value(x15))
        print('x32 = %i' % solver.Value(x32))
        print('x34 = %i' % solver.Value(x34))
        print('x35 = %i' % solver.Value(x35))
        print('x56 = %i' % solver.Value(x56))
        print('x62 = %i' % solver.Value(x62))
        print('x64 = %i' % solver.Value(x64))
    else:
        print('no feasiable soultion')

SimpleSatProgram()