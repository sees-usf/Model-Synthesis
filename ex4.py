## example solver for trace-1 with split CGs (more constraint encoding experiments)

from z3 import *

x1 = Int("x1")
x21 = Int("x21")
x22 = Int("x22")
x3 = Int("x3")
x41 = Int("x41")
x42 = Int("x42")
x51 = Int("x51")
x52 = Int("x52")
x61 = Int("x61")
x62 = Int("x62")

x1_21 = Int("x1_21")
x1_51 = Int("x1_51")
x1_41 = Int("x1_41")
x51_61 = Int("x51_61")
x61_21 = Int("x61_21")
x61_41 = Int("x61_41")

x3_22 = Int("x3_22")
x3_52 = Int("x3_52")
x3_42 = Int("x3_42")
x52_62 = Int("x52_62")
x62_22 = Int("x62_22")
x62_42 = Int("x62_42")

s = Solver()

## node constraints for DAG 1
s.add(x1==3)
s.add(x21<=3, 0 <= x21)
s.add(x41<=2, 0 <= x41)
s.add(x51<=3, 0 <= x51)
s.add(x61<=3, 0 <= x61)
#
## edge constraints for DAG 1
s.add(x1_21 <=3, 0 <= x1_21)
s.add(x1_51 <=3, 0 <= x1_51)
s.add(x1_41 <=2, 0 <= x1_41)
s.add(x51_61 <= 3, 0 <= x51_61)
s.add(x61_21 <= 3, 0 <= x61_21)
s.add(x61_41 <= 2, 0 <= x61_41)
#
## joint node/edge constraints for DAG 1
s.add(x1 == (x1_21 + x1_41 + x1_51))
s.add(x1_51 == x51, x51 == x51_61)
s.add(x51_61 == x61, x61 == (x61_21 + x61_41))
s.add(x21 == (x1_21 + x61_21))
s.add(x41 == (x61_41 + x1_41))

## node constraints for DAG 2
s.add(x3==2)
s.add(x22<=3, 0 <= x22)
s.add(x42<=2, 0 <= x42)
s.add(x52<=2, 0 <= x52)
s.add(x62<=2, 0 <= x62)
#
## edge constraints for DAG 2
s.add(x3_22<=2, 0 <= x3_22)
s.add(x3_52<=2, 0 <= x3_52)
s.add(x3_42<=2, 0 <= x3_42)
s.add(x52_62 <= 2, 0 <= x52_62)
s.add(x62_22 <= 2, 0 <= x62_22)
s.add(x62_42 <= 2, 0 <= x62_42)
#
## joint node/edge constraints for DAG 2
s.add(x3 == (x3_22 + x3_42 + x3_52))
s.add(x3_52 == x52, x52 == x52_62)
s.add(x52_62 == x62, x62 == (x62_22 + x62_42))
s.add(x22 == (x3_22 + x62_22))
s.add(x42 == (x62_42 + x3_42))

## unified constraints for all DAGs based on mining results from trace
s.add((x51 + x52) == 3, (x61 + x62) == 3, (x41 + x42) == 2, (x21 + x22) == 3)
s.add((x51_61 + x52_62) <= 3, (x51_61 + x52_62) >= 0)
s.add((x61_21 + x62_22) <= 3, (x61_21 + x62_22) >= 0)
s.add((x61_41 + x62_42) <= 2, (x61_41 + x62_42) >= 0)


## User constraints
#s.add(x41 == 0)
#s.add(x22 == 0)


s.check()
old_m = s.model()

print("x1_21 =", old_m[x1_21], "x1_41 =", old_m[x1_41], "x1_51 =", old_m[x1_51], "x51_61 =", old_m[x51_61], "x61_21 =", old_m[x61_21], "x61_41 =", old_m[x61_41])
print("x3_22 =", old_m[x3_22], "x3_42 =", old_m[x3_42], "x3_52 =", old_m[x3_52], "x52_62 =", old_m[x52_62], "x62_22 =", old_m[x62_22], "x62_42 =", old_m[x62_42])
print("-----")
s.add(Or(x1_21 != old_m[x1_21], x1_41 != old_m[x1_41], x1_51 != old_m[x1_51], x51_61 != old_m[x51_61], x61_21 != old_m[x61_21], x61_41 != old_m[x61_41]))
s.add(Or(x3_22 != old_m[x3_22], x3_42 != old_m[x3_42], x3_52 != old_m[x3_52], x52_62 != old_m[x52_62], x62_22 != old_m[x62_22], x62_42 != old_m[x62_42]))


while s.check() == sat:
        m = s.model()
        print("x1_21 =", m[x1_21], "x1_41 =", m[x1_41], "x1_51 =", m[x1_51], "x51_61 =", m[x51_61], "x61_21 =", m[x61_21], "x61_41 =", m[x61_41])
        print("x3_22 =", m[x3_22], "x3_42 =", m[x3_42], "x3_52 =", m[x3_52], "x52_62 =", m[x52_62], "x62_22 =", m[x62_22], "x62_42 =", m[x62_42])
        print("-----")
        #
        ## individual constraints for separate CGs
        #s.add(Or(And(m[x1_21] > 0, x1_21 == 0), And(m[x1_41] > 0, x1_41 == 0), And(m[x1_51] > 0, x1_51 == 0), And(m[x51_61] > 0, x51_61 == 0), And(m[x61_41] > 0, x61_41 == 0), And(m[x61_21] > 0, x61_21 == 0)))
        #s.add(Or(And(m[x3_22] > 0, x3_22 == 0), And(m[x3_42] > 0, x3_42 == 0), And(m[x3_52] > 0, x3_52 == 0), And(m[x52_62] > 0, x52_62 == 0), And(m[x62_42] > 0, x62_42 == 0), And(m[x62_22] > 0, x62_22 == 0)))
       
        ## unified constraints for both CGs.
        #s.add(Or(And(m[x1_21] > 0, x1_21 == 0), And(m[x1_41] > 0, x1_41 == 0), And(m[x1_51] > 0, x1_51 == 0), And(m[x51_61] > 0, x51_61 == 0), And(m[x61_41] > 0, x61_41 == 0), And(m[x61_21] > 0, x61_21 == 0), And(m[x3_22] > 0, x3_22 == 0), And(m[x3_42] > 0, x3_42 == 0), And(m[x3_52] > 0, x3_52 == 0), And(m[x52_62] > 0, x52_62 == 0), And(m[x62_42] > 0, x62_42 == 0), And(m[x62_22] > 0, x62_22 == 0)))
       
        ## Weak constraints for individual CGs
        #s.add(Or(x1_21 != m[x1_21], x1_41 != m[x1_41], x1_51 != m[x1_51], x51_61 != m[x51_61], x61_21 != m[x61_21], x61_41 != m[x61_41]))
        #s.add(Or(x3_22 != m[x3_22], x3_42 != m[x3_42], x3_52 != m[x3_52], x52_62 != m[x52_62], x62_22 != m[x62_22], x62_42 != m[x62_42]))
        #s.add(Or(x51 != m[x51], x52 != m[x52], x61 != m[x61], x62 != m[x62], x21 != m[x21], x22 != m[x22], x41 != m[x41], x42 != m[x42]))


        #s.add(Or(old_m[x1_21] != m[x1_21], x1_21 != m[x1_21]))
        #s.add(Or(old_m[x1_41] != m[x1_41], x1_41 != m[x1_41]))
        #s.add(Or(old_m[x1_51] != m[x1_51], x1_51 != m[x1_51]))
        #s.add(Or(old_m[x51_61] != m[x51_61], x51_61 != m[x51_61]))
        #s.add(Or(old_m[x61_21] != m[x61_21], x61_21 != m[x61_21]))
        #s.add(Or(old_m[x61_41] != m[x61_41], x61_41 != m[x61_41]))

        #s.add(Or(old_m[x3_22] != m[x3_22], x3_22 != m[x3_22]))
        #s.add(Or(old_m[x3_42] != m[x3_42], x3_42 != m[x3_42]))
        #s.add(Or(old_m[x3_52] != m[x3_52], x3_52 != m[x3_52]))
        #s.add(Or(old_m[x52_62] != m[x52_62], x52_62 != m[x52_62]))
        #s.add(Or(old_m[x62_22] != m[x62_22], x62_22 != m[x62_22]))
        #s.add(Or(old_m[x62_42] != m[x62_42], x62_42 != m[x62_42]))

        s.add(Or(And(old_m[x1_21] == m[x1_21], x1_21 != m[x1_21]), And(old_m[x1_41] == m[x1_41], x1_41 != m[x1_41]), And(old_m[x1_51] == m[x1_51], x1_51 != m[x1_51]), And(old_m[x51_61] == m[x51_61], x51_61 != m[x51_61]), And(old_m[x61_21] == m[x61_21], x61_21 != m[x61_21]), And(old_m[x61_41] == m[x61_41], x61_41 != m[x61_41])))
        s.add(Or(And(old_m[x3_22] == m[x3_22], x3_22 != m[x3_22]), And(old_m[x3_42] == m[x3_42], x3_42 != m[x3_42]), And(old_m[x3_52] == m[x3_52], x3_52 != m[x3_52]), And(old_m[x52_62] == m[x52_62], x52_62 != m[x52_62]), And(old_m[x62_22] == m[x62_22], x62_22 != m[x62_22]), And(old_m[x62_42] == m[x62_42], x62_42 != m[x62_42])))
       