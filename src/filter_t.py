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
    InProgress = 7
    CheckNext = 8
    Stay = 9
    # different end states
    Matched = 4
    Bad = 5
    Final = 6
    Unknown = 10



ConstrVacuous = 0   # Does not match the first input_msg
ConstrMatched = 1   # Match all input_msg as specified
ConstrBad = 2       # Mismatch an input_msg after matching some previous input_msg
ConstrProgress = 3  # Partially match some input_msg as specified


# @input: a sequence of msg index, op inlcuding '*', '+', and ';'
class filter_t:

    def __init__(self, constr):
        self.constr_table = {0:[]}
        self.initial_state = 0
        self.final_states = []
        self.cur_state = 0
        self.STATE = ConstrState.Unknown

        #@ build a FA from input 'constr'
        index = 0
        final_index = -1
        count = 0
        for c in constr:
            count += 1
            cur_msg = c[0]
            cur_op = c[1]
            if cur_op == '1':
                self.constr_table[index].append([cur_msg, index+1])
                index += 1
                self.constr_table[index] = []
                final_index = index
            elif cur_op == '*':
                self.constr_table[index].append([cur_msg, index])
                if count < len(constr):
                    self.constr_table[index].append([-9999, index+1])
                    index += 1
                    self.constr_table[index] = []
                final_index = index
            elif cur_op == '+':
                self.constr_table[index].append([cur_msg, index+1])
                index += 1
                self.constr_table[index] = [[cur_msg, index]]
                if count < len(constr):
                    self.constr_table[index].append([-9999, index+1])
                    index += 1
                    self.constr_table[index] = []
                final_index = index

        self.final_states.append(final_index)
        #@-----------------------------------


    def initialize(self):
        self.STATE = ConstrState.Unknown
        self.cur_state = 0


    def check(self, input_msg):
        if self.STATE == ConstrState.Bad or self.STATE == ConstrState.Final:
            return self.STATE

        if self.cur_state not in self.constr_table:
            print("constr_t.check(), cur_index", self.cur_state, ' does not exist')

        transitions = self.constr_table[self.cur_state]
        if not transitions:
            print("constr_t.check(), bad cur_index", self.cur_state, ' no transitions')

        match_states = []
        self.check_state(input_msg, self.cur_state, match_states)

        if not match_states: # no matching states
            self.STATE = ConstrState.Bad
            return ConstrState.Bad

        next_state = -1
        for s in match_states:
            next_state = next_state if next_state > s else s

        if next_state == -1:
            print("constr_t.check(), next_index -1 is wrong")
            self.STATE = ConstrState.Bad
            return ConstrState.Bad

        self.cur_state = next_state

        if next_state not in self.final_states:
            self.STATE = ConstrState.InProgress
            return ConstrState.InProgress
            
        self.STATE = ConstrState.Final
        return ConstrState.Final


        
    def check_state(self, input_msg, cur_state, match_states):
        if cur_state not in self.constr_table:
            print("constr_t.check(), state index", cur_state, ' does not exist')

        transitions = self.constr_table[cur_state]
        if not transitions:
            print("constr_t.check(), bad state index", cur_state, ' no transitions')

        for t in transitions:
            t_msg = t[0]
            t_next = t[1]
            if t_msg == -1 or t_msg == input_msg:
                match_states.append(t_next)
            elif t_msg == -9999:
                if t_next not in self.final_states:
                    self.check_state(input_msg, t_next, match_states)
        

    # def check(self, input_msg):
    #     if self.state == ConstrState.Matched or self.state == ConstrState.Bad:
    #         return self.state

    #     print(input_msg, '  ', self.cur_index)

    #     cur_msg = self.constraint[self.next_index][0]
    #     cur_op = self.constraint[self.next_index][1]

    #     msg_match = False
    #     if cur_msg == -1 or cur_msg == input_msg: # -1: arbitary message
    #         msg_match = True

        

    #     next_state = None
    #     if self.state == ConstrState.Initial:
    #         if cur_msg != input_msg:
    #             next_state = ConstrState.Bad
    #         elif next_symbol == '*': 
    #             next_state = ConstrState.CheckStar
    #         elif next_symbol == '+': 
    #             next_state = ConstrState.CheckPlus0
    #         elif next_symbol == ';': 
    #             next_state = ConstrState.Matched
    #         else:
    #             self.cur_msg = next_symbol
    #             next_state = ConstrState.CheckZero

    #     elif self.state == ConstrState.CheckZero:
    #         if cur_msg != input_msg:
    #             next_state = ConstrState.Bad
    #         elif next_symbol == '*': 
    #             next_state = ConstrState.CheckStar
    #         elif next_symbol == '+': 
    #             next_state = ConstrState.CheckPlus0
    #         elif next_symbol == ';': 
    #             next_state = ConstrState.Matched
    #         else:
    #             self.cur_msg = next_symbol
    #             next_state = ConstrState.CheckZero

    #     elif self.state == ConstrState.CheckStar:
    #         if cur_msg != input_msg:
    #             next_state = ConstrState.CheckStar
    #         elif next_symbol == '*': 
    #             next_state = ConstrState.CheckStar
    #         elif next_symbol == '+': 
    #             next_state = ConstrState.CheckPlus0
    #         elif next_symbol == ';': 
    #             next_state = ConstrState.Matched
    #         else: 
    #             self.cur_msg = next_symbol
    #             next_state = ConstrState.CheckZero
                
    #     elif self.state == ConstrState.CheckPlus0:
    #         next_state = ConstrState.CheckPlus

    #     elif self.state == ConstrState.CheckPlus:
    #         if cur_msg != input_msg:
    #              next_state = ConstrState.CheckPlus
    #         elif next_op == '*': 
    #              next_state = ConstrState.CheckStar
    #         elif next_op == '+': 
    #              next_state = ConstrState.CheckPlus0
    #         elif next_op == ';': 
    #              next_state = ConstrState.Matched
    #         else:
    #             self.cur_msg = next_symbol 
    #             next_state = ConstrState.CheckZero

    #     elif self.state == ConstrState.Matched:
    #         next_state = ConstrState.Matched       

    #     elif self.state == ConstrState.Bad:
    #         next_state = ConstrState.Bad

        
    #     # finish the state transition
    #     if next_state != ConstrState.Bad and next_state != ConstrState.Matched:   
    #         if self.state != ConstrState.CheckPlus0 and cur_msg == input_msg:
    #             self.next_index += 2
            

    #     self.state = next_state
    #     print(self.state, '  ', self.next_index,'------')

    #     #@ next_state == END
    #     return self.state


