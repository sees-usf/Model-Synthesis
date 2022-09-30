# Laith Abdel-Rahman

# Import PuLP, install using `pip install pulp`
import pulp as pl

# The problem model called ex1, will find the minimal solution
model = pl.LpProblem('ex1', pl.LpMinimize)

# Node Constraints
x1 = pl.LpVariable('x1', 2, 2)
x2 = pl.LpVariable('x2', 2, 2)
x3 = pl.LpVariable('x3', 2, 2)
x4 = pl.LpVariable('x4', 2, 2)
x5 = pl.LpVariable('x5', 2, 2)
x6 = pl.LpVariable('x6', 2, 2)

# Edge Constraints
x12 = pl.LpVariable('x12', 0, 2)
x14 = pl.LpVariable('x14', 0, 2)
x15 = pl.LpVariable('x15', 0, 2)

x32 = pl.LpVariable('x32', 0, 2)
x34 = pl.LpVariable('x34', 0, 2)
x35 = pl.LpVariable('x35', 0, 1)

x56 = pl.LpVariable('x56', 0, 2)

x62 = pl.LpVariable('x62', 0, 2)
x64 = pl.LpVariable('x64', 0, 2)

# Origin Node Support constraints
model += x1 == (x12 + x14 + x15)
model += x3 == (x32 + x34 + x35)
model += x5 == x56
model += x6 == (x62 + x64)

# Destination Node Support constraints
model += x2 == (x12 + x32 + x62)
model += x4 == (x64 + x34 + x14)
model += x5 == (x15 + x35)
model += x6 == x56

# PuLP solves the constraint satisfaction problem
status = model.solve()

# Prints whether the solution is optimal or infeasible
print(pl.LpStatus[status])

# Solution for Node Supports
print(
      'x1 = ' + str(pl.value(x1)),
      'x2 = ' + str(pl.value(x2)),
      'x3 = ' + str(pl.value(x3)),
      'x4 = ' + str(pl.value(x4)),
      'x5 = ' + str(pl.value(x5)),
      'x6 = ' + str(pl.value(x6))
)

# Solution for Edge Supports
print(
      'x12 = ' + str(pl.value(x12)),
      'x14 = ' + str(pl.value(x14)),
      'x15 = ' + str(pl.value(x15)),
      'x32 = ' + str(pl.value(x32)),
      'x34 = ' + str(pl.value(x34)),
      'x35 = ' + str(pl.value(x35)),
      'x56 = ' + str(pl.value(x56)),
      'x62 = ' + str(pl.value(x62)),
      'x64 = ' + str(pl.value(x64))
)
