from src.logging import *
from src.filter_t import *

class MatchState(Enum):
    MatchEx = 0
    MatchInc = 1
    MatchNone = 2


class filter_list:

    def __init__(self, file_name):
        self.excludes = []
        self.includes = []
        self.read_file(file_name)
    
    def read_file(self, filters_filename):
        try:
            filters_f = open(filters_filename, 'r')
        except IOError as e:
            print("Couldn't open file (%s)." % e)
            return

        lines = filters_f.readlines()
        INPUT_IDLE = 0
        INPUT_EXCLUDE = 1
        INPUT_INCLUDE = 2
        parse_state = INPUT_IDLE
        for line in lines:
            line = line.rstrip("\n")
            if line[0] == '#':
                if line.lower() == '#include': 
                    parse_state = INPUT_INCLUDE
                elif line.lower() == '#exclude': 
                    parse_state = INPUT_EXCLUDE
                else:
                    log('Unrecognized section %s in filters file %s' %(line, filters_filename))
                    return
                continue

            filter = line.split()
            pattern = []
            for ele in filter:
                op = '1'
                idx = ele
                if ele[-1]=='*':
                    op = '*'
                    idx = ele[0:len(ele)-1]
                elif ele[-1] == '+':
                    op = '+'
                    idx = ele[0:len(ele)-1]

                idx = '-1' if idx == '-' else idx

                pattern.append([int(idx), op])

            if parse_state == INPUT_EXCLUDE:
                self.excludes.append(filter_t(pattern))
            elif parse_state == INPUT_INCLUDE:
                self.includes.append(filter_t(pattern))

        log('filters are empty', WARN) if len(self.includes)==0 and len(self.excludes)==0 else None

        
    # Return False -- constraints not sat: any exclude matched, or none of includes matched
    # Return True  -- otherwise 
    def check(self, in_seq):
        for msg in in_seq:
            # if any exclude constraint matched, return false 
            match_exclude = False
            for constr_ex in self.excludes:
                ex_state = constr_ex.check(msg)
                if ex_state == ConstrState.Final:
                    match_exclude = True
                    break
                    #     return MatchState.MatchEx
                    # elif ex_state == ConstrState.Bad:
                    #     return MatchState.MatchNone       

            match_include = False
            for constr_in in self.includes:
                inc_state = constr_in.check(msg)
                if msg == in_seq[-1] and inc_state == ConstrState.Final:
                    match_include = True
                    break
                    # elif inc_state == ConstrState.Bad:
                    #     return MatchState.MatchNone       

        if match_include and match_exclude:
            print('constraints_t@101: current sequence match to both exclude and include filters ... exit')
            exit()
                
        if match_exclude:
            return MatchState.MatchEx
        if match_include:
            return MatchState.MatchInc
        return MatchState.MatchNone


    def initialize(self):
        for c in self.excludes:
            c.initialize()
        for c in self.includes:
            c.initialize()

    
    def test(self):
        # an example pattern for testing 0 -* 36
        pat = [['0', '1'], ['-1', '*'], ['36', '1']]
        constr_ex = constr_t(pat)
        self.includes.append(constr_ex)
        print(self.includes)

        # an example sequence for testing
        in_seq = [0, 27, 10, 17, 19, 13, 36]
        status = self.check(in_seq)
        print(status)
