# #exclude
# M1 0|*|+ M2 0|*|+ M3  # 0: M1 M2 are are immediate one after the other; *(+): between M1 and M2, there are zero (one) or more other messages. 

# M1@source=cpu0 0|*|+ M2@command=rd …


# pattern_t:
# List (sequence): key=msg_index, value =[op, msg_index]


# initial state, cur_msg = first_msg


# Check(input_msg): input_msg passed every time this function is invoked.

# state == initial state && cur_msg = input_msg -> cur_msg = next_msg in the list, get op.
# op == 0: state = checkZero
# op == *: state = checkStar
# op == +: state = checkPlus


# state == checkZero && 
# cur_msg == input_msg: cur_msg = next_msg in the list, get op
# op == 0: state = checkZero
# op == *: state = checkStar
# op == +: state = checkPlus
# else: return false

# State == checkStar &&
# cur_msg == input_msg -> cur_msg = next_msg in the list, get op
# op == 0: state = checkZero
# op == *: state = checkStar
# op == +: state = checkPlus
# cur_msg != input_msg -> skip

# state == checkPlus && cur_msg == input_msg -> cur_msg == next_msg in the list, get op, 
# op == 0: state = checkZero
# op == *: state = checkStar
# op == +: state = checkPlus

# When the end of constraint is reached, return true # input sequence meets the pattern
# Otherwise, return false.

from src.logging import *
from enum import Enum
class ConstrState(Enum):
    Initial = 0
    CheckZero = 1
    CheckStar = 2
    CheckPlus0 = 3
    CheckPlus = 3
    # different end states
    Matched = 4
    Bad = 5
    Vacuous = 6


ConstrVacuous = 0   # Does not match the first input_msg
ConstrMatched = 1   # Match all input_msg as specified
ConstrBad = 2       # Mismatch an input_msg after matching some previous input_msg
ConstrProgress = 3  # Partially match some input_msg as specified


# @input: a sequence of msg index, op inlcuding '*', '+', and ';'
class constr_t:

    def __init__(self, constr):
        self.constraint = constr
        self.next_index = 0
        self.state = ConstrState.Initial

        cur_msg = self.constraint[self.next_index]
        if cur_msg == '*':
            self.state = ConstrState.CheckStar
            self.next_index += 1
        elif cur_msg == '+':
            self.state = ConstrState.CheckPlus0
            self.next_index += 1
        elif cur_msg == ';':
            self.state = ConstrState.Matched
        else:
            self.state = ConstrState.CheckZero



    def check(self, input_msg):
        if self.state == ConstrState.Matched or self.state == ConstrState.Bad:
            return self.state

        print(input_msg, '  ', self.next_index)

        cur_msg = self.constraint[self.next_index]
        next_symbol = self.constraint[self.next_index+1]


        next_state = None
        if self.state == ConstrState.Initial:
            if cur_msg != input_msg:
                next_state = ConstrState.Bad
            elif next_symbol == '*': 
                next_state = ConstrState.CheckStar
            elif next_symbol == '+': 
                next_state = ConstrState.CheckPlus0
            elif next_symbol == ';': 
                next_state = ConstrState.Matched
            else:
                self.cur_msg = next_symbol
                next_state = ConstrState.CheckZero

        elif self.state == ConstrState.CheckZero:
            if cur_msg != input_msg:
                next_state = ConstrState.Bad
            elif next_symbol == '*': 
                next_state = ConstrState.CheckStar
            elif next_symbol == '+': 
                next_state = ConstrState.CheckPlus0
            elif next_symbol == ';': 
                next_state = ConstrState.Matched
            else:
                self.cur_msg = next_symbol
                next_state = ConstrState.CheckZero

        elif self.state == ConstrState.CheckStar:
            if cur_msg != input_msg:
                next_state = ConstrState.CheckStar
            elif next_symbol == '*': 
                next_state = ConstrState.CheckStar
            elif next_symbol == '+': 
                next_state = ConstrState.CheckPlus0
            elif next_symbol == ';': 
                next_state = ConstrState.Matched
            else: 
                self.cur_msg = next_symbol
                next_state = ConstrState.CheckZero
                
        elif self.state == ConstrState.CheckPlus0:
            next_state = ConstrState.CheckPlus

        elif self.state == ConstrState.CheckPlus:
            if cur_msg != input_msg:
                 next_state = ConstrState.CheckPlus
            elif next_op == '*': 
                 next_state = ConstrState.CheckStar
            elif next_op == '+': 
                 next_state = ConstrState.CheckPlus0
            elif next_op == ';': 
                 next_state = ConstrState.Matched
            else:
                self.cur_msg = next_symbol 
                next_state = ConstrState.CheckZero

        elif self.state == ConstrState.Matched:
            next_state = ConstrState.Matched       

        elif self.state == ConstrState.Bad:
            next_state = ConstrState.Bad

        
        # finish the state transition
        if next_state != ConstrState.Bad and next_state != ConstrState.Matched:   
            if self.state != ConstrState.CheckPlus0 and cur_msg == input_msg:
                self.next_index += 2
            

        self.state = next_state
        print(self.state, '  ', self.next_index,'------')

        #@ next_state == END
        return self.state


