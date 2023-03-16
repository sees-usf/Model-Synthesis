from z3 import *


class peterson:
    def __init__(self):
        # Defining variables
        x = Int("x{0}".format(0))       
        b1 = Bool("b1{0}".format(0))
        b2 = Bool("b2{0}".format(0))
        st1 = Int("st1{0}".format(0))
        st2 = Int("st2{0}".format(0))

        # define the initial state
        init_state = And(st1 == 1, b1 == False, st2 == 0, b2 == False)
        
        
    def getInitState(self):
        return self.init_state


    # define property for step k
    def getProperty(self, k):
        st1 = Int("st1{0}".format(k))
        st2 = Int("st2{0}".format(k))
        P = Not(And(st1 == 3, st2== 3))
        return P


    # shold return variables and their types?
    def getVariables(self):
        return ["x", "st1", "st2", "b1", "b2"]


    def getTransitions(self, k):
        # Defining states - original
        # Defining states - prime
        x = Int("x{0}".format(k))       
        b1 = Bool("b1{0}".format(k))
        b2 = Bool("b2{0}".format(k))
        st1 = Int("st1{0}".format(k))
        st2 = Int("st2{0}".format(k))

        xPrime = Int("x{0}".format(k + 1))
        b1Prime = Bool("b1{0}".format(k + 1))
        b2Prime = Bool("b2{0}".format(k + 1))
        st1_next = Int("st1{0}".format(k + 1))
        st2_next = Int("st2{0}".format(k + 1))

        T1 = And(Implies(st1 == 0, st1_next == 1),
                 Implies(st1 == 1, And(b1Prime == True, xPrime == 2, st1_next == 2)),
                 Implies(And(st1 == 2, Or(x == 1, b2 == False)), st1_next == 3),
                 Implies(And(st1 == 2, Not(Or(x == 1, b2 == False))), st1_next == 2),
                Implies(st1 == 3, And(b1Prime == False, st1_next == 0))
                 )

        T2 = And(Implies(st2 == 0, st2_next == 1),
                 Implies(st2 == 1, And(b2Prime == True, xPrime == 2, st2_next == 2)),
                 Implies(And(st2 == 2, Or(x == 1, b1 == False)), st2_next == 3),
                 Implies(And(st2 == 2, Not(Or(x == 1, b1 == False))), st2_next == 2),
                Implies(st2 == 3, And(b2Prime == False, st2_next == 0))
                )

        T = Or(And(T1, st2 == st2_next),
               And(T2, st1 == st1_next))

        return T


    