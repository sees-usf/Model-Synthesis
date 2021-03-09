import re, os, random, sys
from datetime import datetime
# from uml_graph import *
import pygraphviz as pgv

class Vertex:
    def __init__(self, node, label):
        self.id = node
        self.adjacent = {}
        self.label = label

    def __str__(self):
        return str(self.id) + ' adjacent: ' + str([x.id for x in self.adjacent])

    def add_neighbor(self, neighbor, weight=0):
        self.adjacent[neighbor] = weight

    def remove_neighbor(self, neighbor):
        self.adjacent.pop(neighbor)

    def get_connections(self):
        # print("key",self,self.adjacent.keys())
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

class Graph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node,label):
        self.num_vertices = self.num_vertices + 1
        new_vertex = Vertex(node,label)
        self.vert_dict[node] = new_vertex
        return new_vertex

    def remove_vertex(self, node):
        self.num_vertices = self.num_vertices -1
        self.vert_dict.pop(node)


    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, cost = 0):
        if frm not in self.vert_dict:
            self.add_vertex(frm)
        if to not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm].add_neighbor(self.vert_dict[to], cost)
        # self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)
    def remove_edge(self,child,parent):

        # print(child, parent, "Remove edge: ",self.vert_dict[parent], self.vert_dict[child])
        self.vert_dict[parent].remove_neighbor(self.vert_dict[child])
        # self.vert_dict.pop(child)


    def get_vertices(self):
        return self.vert_dict.keys()

    def get_leaves(self):
        leaves = []
        for k in self.vert_dict:
            if self.vert_dict[k].get_connections():
                pass
            else:
                # print("no manchis", k, self.vert_dict[k].get_connections())
                # print(type(k))
                leaves.append(k)
        return leaves

class Planter:
    patterns = []
    map_info ={}
    start_event = []
    end_event = []
    CG = {}
    msg_file = ''
    sol_file = ''
    edges = []
    prefix = []
    prev_random = []
    msg_def = {}
    causality_graph = Graph()

    def rn(self):
        while (True):
            rand = random.randint(0, 2000)
            if rand not in self.prev_random:
                self.prev_random.append(rand)
                return rand
        return -1

    def map_function(self, file):
        # global map_info
        start_ends = []
        start_events = []
        end_events = []
        lines = open(file).read().splitlines()

        with open(file, "r", encoding='utf-8-sig') as fileobj:
            for i, line in enumerate(fileobj):
                if line == "#\n" or line =="#":
                    start_ends.append(i)
                else:
                    temp = line.split(":")
                    msg = [i.replace(" ","") for i in temp[1:]]
                    # self.map_info[int(temp[0])] = str(msg[0])+":"+str(msg[1])+":"+str(msg[2])+":"+str(msg[3][:-1])
                    self.map_info[int(temp[0])] = [str(msg[0]), str(msg[1]), str(msg[2])+":"+str(msg[3][:-1])]

        if len(start_ends)>=2:
            start_events = lines[start_ends[0]:start_ends[1]]
        if len(start_ends)>=4:
            end_events = lines[start_ends[2]:start_ends[3]]

        if len(self.start_event) == 0:
            for line in start_events:
                if line == "#\n" or line == "#":
                    pass
                else:
                    temp = line.split(":")
                    self.start_event.append(int(temp[0]))
        else:
            print("Start events specified by the user: ", self.start_event)

        if len(self.end_event) == 0:
            for line in end_events:
                if line == "#\n" or line == "#":
                    pass
                else:
                    temp = line.split(":")
                    self.end_event.append(int(temp[0]))
            print("End events specified by the user: ", self.end_event)
        else:
            print("End events specified by the user: ", self.end_event)

        # return self.map_info

    def parse_seqs(self,file):
        seqs = open(file).read()
        new_str = re.sub('[^a-zA-Z0-9\n\.]', ' ', seqs)
        open('b.txt', 'w').write(new_str)

        # patterns = []
        with open('b.txt', "r", encoding='utf-8-sig') as f:
            lines = [line.strip() for line in f.readlines()]
            for line in lines:
                temp = (line.split(" "))
                temp = [int(i) for i in temp if len(i)]
                if temp[0:len(self.prefix)] == self.prefix:# and temp[-1] in self.end_event:
                    if self.end_event:
                        if temp[-1] in self.end_event:
                            self.patterns.append(temp)
                    else:
                        self.patterns.append(temp)
        os.remove('b.txt')

    # parse_seqs('sol-sequences.txt', [0, 18, 10])
    # print(len(patterns), patterns)

    # a = {0:['seq1',10,[1]], 1:[0,11,[2]], 2:[1,12,[3]], 3:[2,13,[4]], 4:[3,17,[5]], 5:[4, 18,[]]}
    # b = {6:['seq2',10,[7]], 7:[6,11,[8]], 8:[7,13,[9]], 9:[8,17,[10]], 10:[9, 18,[]]}
    def grah_maker(self,b={}):
        self.CG.update(b)
        keys = list(self.CG.keys())

        for i, key1 in enumerate(keys):# enumerate(a):
            for j, key2 in enumerate(keys):
                if key1 in self.CG and key2 in self.CG:
                    if self.CG[key1][1] == self.CG[key2][1] and self.CG[key1][0] == self.CG[key2][0] and i != j: # parent and content are equal; label:parent,content,[childs]
                        child = self.CG[key2][2][0]
                        old_parent = self.CG[key2][0]
                        self.CG[old_parent][2].remove(key2)
                        self.CG[key1][2].append(child)
                        self.CG[child][0] = key1
                        del self.CG[key2]

                    elif 'seq' in str(self.CG[key1][0]) and 'seq' in str(self.CG[key2][0]) and i != j:
                        child = self.CG[key2][2][0]
                        self.CG[key1][2].append(child)
                        self.CG[child][0] = key1
                        del self.CG[key2]

                    else:
                        continue

    # patterns = [[0, 18, 10, 11, 14, 35], [0, 18, 10, 17, 16, 11, 14, 35]]
    # a = {0:['seq1',10,[1]], 1:[0,11,[2]], 2:[1,12,[3]], 3:[2,13,[4]], 4:[3,17,[5]], 5:[4, 18,[]]}

    def seq_to_CG(self):
        j = 0
        # msgs = []
        print(f'\n{len(self.patterns)} sequences found for the given prefix.\n')
        for k, pat in enumerate(self.patterns):
            print(pat)
            a_dict = {}
            for i in range(len(pat)):
                # msgs.append(pat[i])
                if i == 0:
                    a_dict[j+i] = ['seq'+str(k), pat[i],[j+i+1]]
                elif i == len(pat) -1:
                    a_dict[j+i] = [j + i-1, pat[i], []]
                else:
                    a_dict[j+i] = [j + i-1, pat[i], [j+i+1]]
            j = j + i + 1
            # print(j, a_dict)
            self.grah_maker(a_dict)

    def edge_producer(self,dct):
        edges = []
        # print(dct)
        for key in dct:
            for child in dct[key][2]:
                edges.append((key, child))
        return edges


    def draw_planter(self, detailed=0):
        descriptor = []
        self.seq_to_CG()
        edges = self.edge_producer(self.CG)
        # print(len(edges))

        if edges:
            now = datetime.now()
            file_str = "diagrams/seq-"+now.strftime("%H-%M-%S")
            # file_str="seq"
            out_file = file_str+".dot"
            with open(out_file, 'w') as f:
                # f.write("@startuml \nhide empty description\n")
                # f.write("[*] -->" + str(edges[0][0]) + "\n")

                f.write("digraph {\n")
                # { id0_cpu0 [color=red]}
                g = Graph()

                def children_group(conections, vertex):
                    groups = []
                    while conections:
                        # list(my_dict.keys())[0]
                        label = conections[0].label
                        weight = vertex.get_weight(conections[0])
                        # print("connections: ",label, weight)
                        vertex_group = [v for v in conections if v.label == label and vertex.get_weight(v) == weight]
                        groups.append(vertex_group)

                        for v in vertex_group:
                            conections.remove(v)
                    return groups


                for i in edges:
                    if detailed == 1:
                    #     # f.write(str(i[0]) + " --> " + str(i[1]) + " : " + str(self.map_info[self.CG[i[0]][1]][2]) + "\n")
                    #     f.write(str(i[0]) + " --> " + str(i[1]) + " : " + str(self.CG[i[0]][1])+":" + str(self.map_info[self.CG[i[0]][1]][2]) + "\n")
                        
                    #     if self.CG[i[1]][1] in self.end_event:
                    #         end_ev = "end"+str(random.randint(0, 200))
                    #         f.write(str(i[1]) + " --> " + end_ev + " : " + str(self.CG[i[1]][1]) + ":" + str(self.map_info[self.CG[i[1]][1]][2]) + "\n")
                    #         descriptor.append(end_ev)
                    #         # print(self.map_info[self.CG[i[1]][1]])
                    #         self.map_info[end_ev] = self.map_info[self.CG[i[1]][1]]

                        # print(i[0],i[1],self.map_info[self.CG[i[0]][1]][0], self.map_info[self.CG[i[0]][1]][1], self.map_info[self.CG[i[0]][1]][2])
                        

                        # f.write(str(i[0]) + " --> " + str(i[1]) + " : " + str(self.CG[i[0]][1])+":" + str(self.map_info[self.CG[i[0]][1]][2]) + "\n")
                        if i[0] not in descriptor:
                            g.add_vertex(str(i[0]), self.map_info[self.CG[i[0]][1]][0])

                        if i[1] not in descriptor: 
                            g.add_vertex(str(i[1]), self.map_info[self.CG[i[0]][1]][1]) 
                        g.add_edge(str(i[0]), str(i[1]),self.map_info[self.CG[i[0]][1]][2])

                        if self.CG[i[1]][1] in self.end_event:
                            rand_end = self.rn()
                            end_ev = "end"+str(rand_end)
                            # f.write(str(i[1]) + " --> " + end_ev + " : " + str(self.CG[i[1]][1]) + ":" + str(self.map_info[self.CG[i[1]][1]][2]) + "\n")
                            # print(self.map_info[self.CG[i[1]][1]][0], end_ev,self.map_info[self.CG[i[1]][1]][1], self.map_info[self.CG[i[1]][1]][2])
                            # if i[1] not in descriptor: 
                            #     g.add_vertex(str(i[1]), self.map_info[self.CG[i[1]][1]][0])
                                # print("event added:", i[1], self.map_info[self.CG[i[1]][1]][0], self.map_info[self.CG[i[1]][1]][2])
                            g.add_vertex(str(rand_end), self.map_info[self.CG[i[1]][1]][1])
                            g.add_edge(str(i[1]), str(rand_end),self.map_info[self.CG[i[1]][1]][2])
                            
                            descriptor.append(end_ev)
                            # print(self.map_info[self.CG[i[1]][1]])
                            self.map_info[end_ev] = self.map_info[self.CG[i[1]][1]]

                        descriptor.append(i[0])
                        descriptor.append(i[1])
                    else:
                        f.write(str(i[0]) + " --> " + str(i[1]) + " : " + "x" + "\n")
                        descriptor.append(i[0])
                        descriptor.append(i[1])


                # for ev in set(descriptor):
                #     if detailed:
                #         if 'end' in str(ev):
                #             f.write(str(ev) + ":" + str(self.map_info[ev][1]) + "\n")
                #         else:
                #             f.write(str(ev) + ":" + str(self.map_info[self.CG[ev][1]][0]) + "\n")
                #     else:
                #         f.write(str(ev) + ":" + str(self.CG[ev][1]) + "\n")

                # f.write(str(edges[-1][1]) + " --> [*]\n")
                # f.write("@enduml")
                # f.close()
                # print(sys.path[1])
                # os.system("java -jar "+"plantuml.jar " + out_file)
                print(f"\nDone! State diagram @{file_str}.png\n")
                print(f'\n___________________Generated dot notations____________________\n')

                # print(g.vert_dict.keys)
                # print(rand_end)
                # g.add_vertex('234', 'xyz')
                # g.add_edge(str(rand_end), '234', 'abcd')

                # print(g.get_vertices())
                # for k in g.vert_dict:
                #     print(k,g.vert_dict[k])
                # print()
                # for v in g:
                #     print ('g.vert_dict[%s]=%s' %(v.get_id(), g.vert_dict[v.get_id()]))

                # for v in g:
                #     for w in v.get_connections():
                #         vid = v.get_id()
                #         wid = w.get_id()
                #         print ('( %s , %s, %s)'  % ( vid, wid, v.get_weight(w)))
                processed = []
                # print(type(g))
                for v in g:
                    if v not in processed:
                        w = list(v.get_connections())
                        # print("Current node Processing: ", v.get_id(), end="   ")
                        # print("Conections: ", len(v.get_connections()))
                        if len(w)>1:
                            groups = children_group(w, v) #conections, vertex
                            for group in groups:
                                if len(group)>1:
                                    for ver in group[1:]:
                                        # print("Node to be removed:", ver.get_id(), "Conections: ",g.vert_dict[ver.get_id()])

                                        ver_conections = list(ver.get_connections())
                                        for vx in ver_conections:
                                            # print("Connected: ",vx.get_id(), " ",group[0].get_id(), end=" |")
                                            g.add_edge(group[0].get_id(), vx.get_id(), ver.get_weight(vx))
                                        # g.remove_edge(v, ver) ## g.remove_edge(child, parent)
                                        # print(ver.get_id(),v.get_id())
                                        # g.remove_edge(ver.get_id(),v.get_id())
                                        try:
                                            g.remove_edge(str(ver.get_id()),str(v.get_id()))
                                            # print( "removed: ",ver.get_id(),v.get_id())
                                        except KeyError as e:
                                            print(ver.get_id(),v.get_id(),ver.label)
                                            # print("Conections: ", len(ver.get_connections()))
                                            break
                                       
                                        # processed.append(ver)
                                        processed.append(ver)


                # print(processed)
                # g.remove_edge('13', '12')
                for v in processed:
                    g.remove_vertex(v.get_id())
                
                # print(g.get_vertices())
                terminals = g.get_leaves()
                
                color = 1
                for v in g:
                    for w in v.get_connections():
                        vl = v.label
                        wl = w.label
                        # print ('%s_%s->%s_%s[label=\"%s\"];'  % (v.get_id(), vl, w.get_id(), wl, v.get_weight(w)))
                        # print ('id%s_%s->id%s_%s[label=\"%s\"];'  % (v.get_id(), vl, w.get_id(), wl, v.get_weight(w)))
                        if color:
                            color = 0
                            f.write("{id"+str(v.get_id())+"_"+str(vl)+"[color=red]}\n")

                        if w.get_id() not in terminals:
                            print ('id%s_%s->id%s_%s[label=\"%s\"];'  % (v.get_id(), vl, w.get_id(), wl, v.get_weight(w)))
                            f.write("id"+str(v.get_id())+"_"+str(vl)+"->id"+str(w.get_id())+"_"+str(wl)+"[label=\""+str(v.get_weight(w))+"\"];\n")
                        else:
                            print ('id%s_%s->%s[label=\"%s\"];'  % (v.get_id(), vl, wl, v.get_weight(w)))
                            f.write("id"+str(v.get_id())+"_"+str(vl)+"->"+str(wl)+"[label=\""+str(v.get_weight(w))+"\"];\n")


                # for v in g:
                #     print ('g.vert_dict[%s]=%s' %(v.get_id(), g.vert_dict[v.get_id()]))
                f.write("}")
            print(f'\n___________________dot notations end____________________\n')
            f.close()

            B = pgv.AGraph(out_file)  # create a new graph from file
            B.layout(prog='dot')  # layout with default (neato)
            B.draw(file_str+".png")  # draw png
            vertices = g.get_vertices()
            print("\nNumber of vertices in the graph(before merging terminals): ",len(vertices))
            os.remove(file_str+".dot")
            print("Wrote "+file_str+".png")    

        else:
            print("No pattern for the specified prefix found!!!")


    def draw(self, detailed = 0):
        if self.prefix:
            print("Producing UML tree for prefixes:", self.prefix)
        else:
            self.prefix = []
            print("Prefix is not specified, using default prefix:", self.prefix)

        if os.path.isfile(self.msg_file):
            self.map_function(self.msg_file)
        else:
            print("Msg file not found, runing with example file: large.msg")
            self.map_function("../src/large.msg")

        if os.path.isfile(self.sol_file):
            self.parse_seqs(self.sol_file)
        else:
            print("Solution file not found, using default with sol-sequences.txt")
            self.parse_seqs("../src/sol-sequences.txt")


        self.draw_planter(detailed)


pt = Planter()
pt.prefix = [] #[0, 18,10, 11] #specify the prefix of the graph, at least one node.
pt.msg_file = 'large.msg' #specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
pt.sol_file = 'sol-sequences.txt'# specify the solution file (default is sol-sequences.txt)
pt.sol_file = 'model.txt'# specify the solution file (default is sol-sequences.txt)
pt.draw(detailed=1) #call the api, detailed = 1 means nodes complete definition, if detailed = 0, only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.