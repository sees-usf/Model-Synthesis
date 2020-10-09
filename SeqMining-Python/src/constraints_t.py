from src.logging import *
from src.constr_t import *

class MatchState(Enum):
    MatchEx = 0
    MatchInc = 1
    MatchNone = 2


class constraints_t:

    def __init__(self, file_name):
        self.excludes = []
        self.includes = []
        self.read_file(file_name)
    
    def read_file(self, file_name):
        pat = [0, '-', 36, ';']
        constr_ex = constr_t(pat)
        self.excludes.append(constr_ex)
        in_seq = [0, 27, 10, 17, 19, 13, 36]
        status = self.check(in_seq)
        print(status)
        # read constraints from file_name to fill excludes/includes


    # Return False -- constraints not sat: any exclude matched, or none of includes matched
    # Return True  -- otherwise 
    def check(self, in_seq):
        for msg in in_seq:
            # if any exclude constraint matched, return false 
            for constr_ex in self.excludes:
                if constr_ex.check(msg) == ConstrState.Matched:
                    return MatchState.MatchEx

            for constr_in in self.includes:
                state = constr_in.check(msg)
                if msg == in_seq[-1] and state == ConstrState.Matched:
                    return MatchState.MatchInc

        return MatchState.MatchNone