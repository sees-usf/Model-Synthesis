import copy
from src.logging import *
from src.solver.split_edge import *
from z3 import *

#@ generate subsets of flows out of the input set of candidate flows extracted 
#@ from an input solution such that each subset can be used to explain the input trace 
#@
class flow_generator:
    def __init__(self, graph, sol):
        self.graph = graph
        self.solution = sol
        self.edge_z3var_list = []
        self.solver = Solver()
        self.feasible = True
        self.new_constr = None
        self.flow_spec = []

        #@ Generate flow specs
        self.flow_list = self.extract_flows(sol)
        # self.print_flows(self.flow_list)
        self.generate_flow_spec()


    def generate_flow_spec(self):
        #@ lookup tables for graph edges and flows in flow_list 
        edge_table = {}
        flow_table = []

        log('edge support in the solution constraints\n', DEBUG)

        #@ initialize the edge lookup tables
        graph_edges = self.graph.get_edges().values()
        for edge in graph_edges:
            edge_z3var = edge.get_z3var()
            edge_support = self.solution[edge_z3var]
            if edge_support.as_long() > 0:
                edge_table[edge] = []
                self.solver.add(edge_z3var == edge_support)
                self.edge_z3var_list.append(edge_z3var)
                log(str(edge_z3var)+ ' == ' + str(edge_support) + '\n', DEBUG)

        #@ create split edges for each flow, and update edge lookup table
        flow_idx = 0
        for flow in self.flow_list:
            i = 0
            s_edge_list = []
            while i < len(flow)-1:
                node_src = flow[i]
                node_dest = flow[i+1]
                edge = self.graph.get_edge(node_src, node_dest)
                s_edge = split_edge(edge, flow_idx)
                edge_table[edge].append(s_edge)
                s_edge_list.append(s_edge)
                i += 1
            flow_table.append(s_edge_list)
            flow_idx += 1

        log('edge and split edges constraints\n', DEBUG)
        #@ Create problem constraints for solver
        for edge in edge_table.keys():
            edge_z3var = edge.get_z3var()
            s_edge_list = edge_table[edge]
            #@ if edge is not present in any flow sequence (the number of its split edges is 0)
            #@ such edge should be excluded by creating a constraint
            if not s_edge_list:  
                self.new_constr = (edge_z3var == 0) if self.new_constr is None else And(self.new_constr, (edge_z3var == 0))
                continue

            sum_z3vars = None
            s = ''
            for s_edge in s_edge_list:
                s_edge_z3var = s_edge.get_z3var()
                if sum_z3vars is None:
                    sum_z3vars = s_edge_z3var
                    s = str(s_edge_z3var) 
                else:
                    sum_z3vars += s_edge_z3var
                    s = s + ' + ' + str(s_edge_z3var) 

            self.solver.add(edge_z3var == sum_z3vars)
            log(str(edge_z3var) + " == " + str(s) + '\n', DEBUG)

        #@ if an edge in the solution is not covered by any flow sequences
        #@ return constraint to exclude such an edge in the future solution.
        if self.new_constr is not None:
            self.new_constr = simplify(self.new_constr)
            self.feasible = False
            return

        log('creating sequence constraints\n', DEBUG)

        #@ Create constraints for each flow sequnece
        for flow in flow_table:
            i = 0
            edge_0_z3var = flow[0].get_z3var()
            self.edge_z3var_list.append(edge_0_z3var)
            self.solver.add(edge_0_z3var >= 0)
            while i < len(flow)-1:
                edge_1_z3var = flow[i].get_z3var()
                edge_2_z3var = flow[i+1].get_z3var()
                i += 1
                self.solver.add(edge_1_z3var == edge_2_z3var)
                log(str(edge_1_z3var) + " == " + str(edge_2_z3var) + '\n', DEBUG)
        
        # log('creating assumptions, one for each sequence\n', DEBUG)
        # #@------------------------------
        # #@ Creating assumptions, one for each sequence
        # assumption_z3vars = []
        # idx = 0
        # for flow in flow_table:
        #     assume_z3var = Bool('A'+ str(idx))
        #     assumption_z3vars.append(assume_z3var)
        #     edge_0_z3var = flow[0].get_z3var()
        #     self.solver.add(assume_z3var == (edge_0_z3var == 0))
        #     log(str(assume_z3var) + " == " + str(edge_0_z3var) + '\n', DEBUG)
        #     idx += 1
            
        # #@TEST of using assumptioins and unsat core
        # print(assumption_z3vars)
        # print(self.solver.check(assumption_z3vars))
        # print(self.solver.unsat_core())
        # unsatcore = self.solver.unsat_core()
        # for assume_var in unsatcore:
        #     assumption_z3vars_copy = assumption_z3vars.copy()
        #     assumption_z3vars_copy.remove(assume_var)
        #     print(assumption_z3vars_copy)
        #     print(self.solver.check(assumption_z3vars_copy))
        #     print(self.solver.unsat_core())
        # exit('@ flow_generator:127')
        # #@------------------------------

        self.feasible = True  #if self.solver.check() == sat else False
        self.new_constr = True if self.new_constr is None else self.new_constr

        iter = 0
        while self.solver.check() == sat:
            model = self.solver.model()
            print('@ flow_generator:140 print model')
            self.print_z3model(model)
            #@ given a model, find out which flow sequence has non-zero support
            zero_flow_list = flow_table.copy()
            non0_flow_list = []
            idx = 0
            for flow in flow_table:
                edge_0_z3var = flow[0].get_z3var()
                if model[edge_0_z3var].as_long() > 0:
                    non0_flow_list.append(self.flow_list[idx])
                    zero_flow_list.remove(flow)
                idx += 1

            self.flow_spec.append(non0_flow_list)
            self.print_flows(non0_flow_list)
            i = input('@ flow_generator:153 continue')

            if not zero_flow_list:
                break
            zero_flow = zero_flow_list[0]
            edge_0_z3var = zero_flow[0].get_z3var()
            constr = (edge_0_z3var > 0)
            iter += 1
            print(iter, '  ', constr)
            self.solver.add(constr)
            i = input('@ flow_generator: continue')
    #@--------------------------------------------------------

    
    # Extract all flows (a sequnece of nodes) from a solution
    def extract_flows(self, solution):
        all_flows = []
        sol_edges = {}
        # nodes = self.graph.get_nodes()
        edges = self.graph.get_edges().values()

        # find all edges that have non-zero support in a solution
        for edge in edges:
            edge_z3var = edge.get_z3var()
            if solution[edge_z3var].as_long() == 0: 
                continue

            src_node = edge.get_source()
            dest_node = edge.get_destination() 
            if src_node in sol_edges:
                sol_edges[src_node].append(dest_node)
            else:
                sol_edges[src_node] = [dest_node]
        
        for e in sol_edges.keys():
            print(e, ' : ', end='')
            for f in sol_edges[e]:
                print(f, ', ', end='')
            print()
        input('continue @ 186: ')
        
        roots = self.graph.get_roots()

        # find all flows starting with every root node
        flow_list = []
        for root in roots.values():
            if root not in sol_edges:  # check if there is a flow starting from this root
                continue
            flow = [root]
            flow_list.append(flow)
        
        flow_list = self.extract_flows_recursive(sol_edges, flow_list, 1)
        return flow_list


    def extract_flows_recursive(self, edges, flow_list, depth):
        if depth == self.graph.get_max_height():
            return flow_list

        new_flow_list = []
        for flow in flow_list:
            last_node = flow[-1]
            
            # if last_node in terminals:
            if self.graph.is_terminal(last_node):
                new_flow_list.append(flow)
                continue

            # if last_node not in edges:  # check if last_node has succ in edges
            #     new_flow_list.append(flow)
            #     continue
            # go_deeper = True
            succ_list = edges[last_node]
            for node in succ_list:
                if node in flow:  # no duplication messages in a flow
                    continue
                # do not include a flow that does not end with a terminal
                elif (not self.graph.is_terminal(node)) and (depth+1 == self.graph.get_max_height()):
                    continue    
                    
                flow_copy = flow.copy()
                flow_copy.append(node)
                new_flow_list.append(flow_copy)                

        return self.extract_flows_recursive(edges, new_flow_list, depth+1)

        # if go_deeper == True:  
        #     return self.extract_flows_recursive(edges, new_flow_list, terminals, depth+1)
        # else:
        #     return new_flow_list


    def print_flows(self, flow_list):
        print('@flow_generator:print_flows:\n')
        for flow in flow_list:
            for node in flow:
                print(node.get_index(), end=' ')
            print()
        print('@flow_generator:print_flows: Total number of sequences: ' + str(len(flow_list)) + '\n')
        input('continue @flow_generator, 246:')

    def is_feasible(self):
        return self.feasible

    def get_new_constr(self):
        return self.new_constr

        
    def get_flow_spec(self):
        return self.flow_spec
        

    def print_z3model(self, m):
        print(self.edge_z3var_list)
        for edge_z3var in self.edge_z3var_list:
            if m[edge_z3var].as_long() != 0:
                print(edge_z3var, '=', m[edge_z3var], ' ', end=' ')
            
        print()







