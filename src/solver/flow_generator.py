import copy
import time
import os
from src.logging import *
from src.solver.split_node import *
from src.solver.sequence_generator import *
from z3 import *

#@ generate subsets of flows out of the input set of candidate flows extracted 
#@ from an input solution such that each subset can be used to explain the input trace 
#@
class flow_generator:
    def __init__(self, graph, z3model):
        self.graph = graph
        self.z3model = z3model
        self.node_z3var_list = []
        self.solver = Solver()
        self.split_seq_list = []
        self.flow_assumption_table = {}
        self.feasible = True

        #@ additional constraints generated when searching for flow specs that 
        #@ help restrict of space of binary sequences in the main loop
        self.node_cover_constraint_list = []
        self.noncycle_constraint_list = []

        #@ the list of possible flow specs found for input 'z3model'
        self.flow_spec = []

        #@ Generate flow specs
        self.generate_flow_spec()
        log('@flow-generator:30  exiting, flow gen number of flow specs found = ' + str(len(self.flow_spec)) + '\n')


    def generate_flow_spec(self):
        
        self.initialize_solver()
        if not self.feasible:
            return     

        # #@TEST of using assumptioins and unsat core
        # print(assumption_z3vars)
        # while self.solver.check(assumption_z3vars) == unsat:
        #     print(self.solver.unsat_core())
        #     unsatcore = self.solver.unsat_core()
        #     for assume_var in unsatcore:
        #         assumption_z3vars_copy = assumption_z3vars.copy()
        #         assumption_z3vars_copy.remove(assume_var)
        #         assumption_z3vars = assumption_z3vars_copy
        #     input('@ flow_generator:141 continue to next solving')

        
        # model = self.solver.model()
        # print('@ flow_generator:140 print model')
        # self.print_z3model(model)
        # #@ given a model, find out which flow sequence has non-zero support
        # zero_flow_list = s_flow_list.copy()
        # non0_flow_list = []
        # idx = 0
        # for flow in s_flow_list:
        #     s_node_0_z3var = flow[0].get_z3var()
        #     if model[s_node_0_z3var].as_long() > 0:
        #         non0_flow_list.append(flow)
        #         zero_flow_list.remove(flow)
        #     idx += 1

        # self.print_flows(non0_flow_list)
        # input('@ flow_generator:158 continue')
        # #@------------------------------

        self.solve_cond()
        # self.solve()

        log(' number of flow specs found = ' + str(len(self.flow_spec)) + '\n', DEBUG)
    #@--------------------------------------------------------


    def initialize_solver(self):
        #@ lookup tables for graph nodes and their split nodes
        s_node_table = {}

        #@ generate sequences allowed by z3model
        seq_gen = sequence_generator(self.graph, self.z3model)
        # seq_gen.print_noncycle_constraints()

        #log('@flow_generator:83: check sequence feasiablility\n', INFO)
        self.noncycle_constraint_list = seq_gen.get_noncycle_constraints()

        log('edge support in the solution constraints\n', DEBUG)
        #@ initialize the split node lookup tables
        graph_nodes = self.graph.get_nodes().values()
        for node in graph_nodes:
            node_z3var = node.get_z3var()
            node_support = node.get_support()
            s_node_table[node] = []
            self.solver.add(node_z3var == node_support)
            log(str(node_z3var)+ ' == ' + str(node_support) + '\n', DEBUG)

        #@ Check if all edges of every flow are allowed by the input solution
        #@ If not, remove that flow from consideration
        legal_seq_list = seq_gen.get_sequence_list()
        for seq in legal_seq_list:
            i = 0
            while i < len(seq)-1:
                node_src = seq[i]
                node_dest = seq[i+1]
                edge = self.graph.get_edge(node_src, node_dest)
                edge_z3var = edge.get_z3var()
                if self.z3model[edge_z3var].as_long() == 0:
                    raise ValueError(edge.get_id(), ' unexpected 0 support edge')
                i += 1
        #@ legal_flow_list should only contain flows whose edges have non-zero support in
        #@ in the input solution.

        log('@flow-generator:112: print candidate flow sequences\n')
        seq_gen.print_sequences()

        #@ create split nodes for each flow, and update split node lookup table
        seq_idx = 0
        s_seq_list = []
        for seq in legal_seq_list:
            i = 0
            s_seq = []
            while i < len(seq):
                g_node = seq[i]
                s_node = split_node(g_node, seq_idx)
                s_node_table[g_node].append(s_node)
                s_seq.append(s_node)
                i += 1
            s_seq_list.append(s_seq)
            seq_idx += 1
        #@ s_seq_list is the list of flows, each of which contains only split nodes


        #log('@ flow_generator:130: creating assumptions, one for each sequence\n', INFO)
        #@------------------------------
        #@ Creating assumptions, one for each sequence
        idx = 0
        for seq in s_seq_list:
            assume_z3var = Bool('A'+ str(idx))
            s_node_0_z3var = seq[0].get_z3var()
            self.flow_assumption_table[assume_z3var] = (assume_z3var == (s_node_0_z3var > 0))
            log(str(assume_z3var) +'==('+ str(s_node_0_z3var) +'>0)\n', DEBUG)
            idx += 1
        #@------------
        

        log('node and split nodes constraints\n', DEBUG)
        #@ Create problem constraints for solver
        for g_node in s_node_table.keys():
            g_node_z3var = g_node.get_z3var()
            s_node_list = s_node_table[g_node]
            #@ if graph node is not present in any flow sequence (the number of its split nodes is 0)
            #@ it indicates that the current solution is infeasible as not all graph nodes can be covered
            #@ by potential flows allowd by the curent solution        
            if not s_node_list:  
                self.feasible = False
                self.create_node_cover_constraints(g_node)
                continue

            sum_z3vars = None
            s = ''
            for s_node in s_node_list:
                s_node_z3var = s_node.get_z3var()
                if sum_z3vars is None:
                    sum_z3vars = s_node_z3var
                    s = str(s_node_z3var) 
                else:
                    sum_z3vars += s_node_z3var
                    s = s + ' + ' + str(s_node_z3var) 

            self.solver.add(g_node_z3var == sum_z3vars)
            log(str(g_node_z3var) + " == " + s + '\n', DEBUG)

        log('creating sequence constraints\n', DEBUG)
        #@ Create constraints for each flow sequnece: supports of every node of a flow are the same
        for s_seq in s_seq_list:
            s_node_0_z3var = s_seq[0].get_z3var()
            self.node_z3var_list.append(s_node_0_z3var)
            self.solver.add(s_node_0_z3var >= 0)
            i = 1
            while i < len(s_seq):
                s_node_z3var = s_seq[i].get_z3var()
                i += 1
                self.solver.add(s_node_z3var == s_node_0_z3var)
                log(str(s_node_z3var) + " == " + str(s_node_0_z3var) + '\n', DEBUG)
        
        self.split_seq_list = s_seq_list
        log('@flow-generator:185 initialization done\n', INFO)
    #@--------------------------------------------


    #@ find sets of sequences that can form flow specs
    def solve_cond(self):
        #@ update solver with assumptions
        assumption_list = []
        for label in self.flow_assumption_table.keys():
            self.solver.add(self.flow_assumption_table[label])
            assumption_list.append(label)

        self.solve_cond_recursive(assumption_list)
    #@ -----------------------

    def solve_cond_recursive(self, assumption_list):
        log(' flow-gen, solving with assumptions...\n', DEBUG)
        log(' assumption size = ' + str(len(assumption_list)), DEBUG)        
        status = self.solver.check(assumption_list)
        if status == sat:
            model = self.solver.model()
            # log('@flow-generator:208: print z3 model', INFO)
            # self.print_z3model(model)
            self.mode2flows(model)
            return

        unsat_core = self.solver.unsat_core()
        log('Unsat core: ' + str(len(self.solver.unsat_core())) + '\n', DEBUG)
        if not unsat_core: 
            return
        
        unsat_core_lookup = set(unsat_core)

        assumption_list_copy = []
        new_constr = False
        for label in assumption_list:
            if label in unsat_core_lookup:
                new_constr = simplify(Or(new_constr, Not(label)))
            else:
                assumption_list_copy.append(label)
        self.solver.add(new_constr)
        self.solve_cond_recursive(assumption_list_copy)


    def solve(self):
        #@ Run the solver to find all combinations of flows that satisfy the constraints created above.
        #@ Run exhautively to find all possbiel combinations of flows.   
        iter = 0
        while self.solver.check() == sat:
            model = self.solver.model()
            log('@ flow_generator:232  SAT --> print model', INFO)
            self.print_z3model(model)

            #@ given a model, find out which flow sequence has non-zero support
            log('@ flow_generator:239 check gen\'ed flows  --> continue', INFO)
            self.mode2flows(model)
    #@----------------------------

    #@ convert the model from the self.solver, and find the set of sequences with
    #@ non-0 support
    def mode2flows(self, seq_model):
        #@ given a model, find out which flow sequence has non-zero support
        s_seq_list_copy = self.split_seq_list.copy()
        flow_list = []
        new_constr = False
        for seq in s_seq_list_copy:
            s_node_0_z3var = seq[0].get_z3var()
            if seq_model[s_node_0_z3var].as_long() > 0:
                flow_list.append(seq)
            else:
                new_constr = simplify(Or(new_constr, (s_node_0_z3var > 0)))

        self.flow_spec.append(flow_list)
        
        log('@%s:%d: check found flow specification\n' % (whoami(), line_numb()), INFO, True)
        self.print_flows(flow_list)


        log('@ flow_generator:242  --> check blocking constraint --> continue to next solving step\n', INFO)
        log(str(new_constr)+'\n', INFO)
        self.solver.add(new_constr)
    #@--------------------

    def print_split_flows(self, flow_list):
        for flow in flow_list:
            for node in flow:
                print(node.get_split_index(), end=' ')
            print()
        print('@flow_generator:print_flows:274 Total number of sequences: ' + str(len(flow_list)) + '\n')

    def print_flows(self, flow_list):
        
                
        abs_path = 'fs-'+ time.asctime(time.localtime(time.time()))+'.txt'
        # sol_path = os.path.join(abs_path, 'Solution')
        # os.makedirs(sol_path, exist_ok=True)
        # sol_file_path = os.path.join(sol_path, 'Solution ' + '.txt')
        f = open(abs_path, 'w')
        for flow in flow_list:
            seq = []
            for node in flow:
                print(node.get_index(), end=' ')
                seq.append(node.get_index())
            print()
            f.write(str(seq)+'\n')
        f.close()
        log('@flow_generator:print_flows:282 Total number of sequences: ' + str(len(flow_list)) + '\n', INFO)

    def is_feasible(self):
        return self.feasible

        
    def get_flow_spec(self):
        return self.flow_spec
        




    def print_z3model(self, m):
        # print(self.node_z3var_list)
        for node_z3var in self.node_z3var_list:
            if m[node_z3var].as_long() != 0:
                print(node_z3var, '=', m[node_z3var], ' ', end=' ')    
        print()


    #@ Input: 'g_node' not covered by the sequences extracted from 'z3model'
    #@ Output: z3 constraint that forces z3 solver to include some incoming edges of 'g_node'
    #@ in the next model, also exclude existing incoming edges of 'g_node' as they are useless
    def create_node_cover_constraints(self, g_node):
        g_node_incoming_edges = g_node.get_incoming_edges()
        constr = None
        for edge in g_node_incoming_edges:
            edge_z3var = edge.get_z3var()
            if self.z3model[edge_z3var].as_long() == 0:
            #     constr = Or(constr, edge_z3var == 0)
            # else:
                constr = (edge_z3var > 0) if constr is None else Or(constr, edge_z3var > 0) 
        if constr is not None: 
            # print(simplify(constr))
            self.node_cover_constraint_list.append(simplify(constr))

    def get_node_cover_constraints(self):
        return self.node_cover_constraint_list

    def get_noncycle_constraints(self):
        return self.noncycle_constraint_list







