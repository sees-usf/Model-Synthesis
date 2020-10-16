import re
import os
import functools
import operator

class Planter:
    start_event = []
    end_event = []
    edges = {}
    map_info = {}
    global_depth = 999
    bin_edge = []
    patterns = []
    visit = []
    old_graph = {}
    new_graph = {}
    msg_file = ''
    support_file = ''

    def causlity_graph(self, edges):
        keys = []
        dt = {}
        for i, j in edges:
            keys.append(i)
            keys.append(j)

        keys = set(keys)
        keys = list(keys)
        keys.sort()
        # print(keys)

        dt = dict.fromkeys(keys, [])

        for key in dt:
            temp = []
            for edge in edges:
                if edge[0] == key:  # and edge[1] not in start_event:
                    temp.append(int(edge[1]))
            dt[key] = temp
        return dt


    def Traverse(self,root, depth, visit, grow):
        # global patterns, terminal
        # print("visit now: ", visit)
        if (depth == self.global_depth) or visit[-1] in self.end_event:
            self.patterns.append(list(visit))
            return
        noNewNode = 1
        for rule in grow:
            node = rule[1]
            if (node not in visit and rule[0] == root):
                visit.append(node)
                noNewNode = 0
                self.Traverse(node, depth+1, visit, grow)
                visit.remove(node)
            # elif node in visit:
            #     all.append(rule)

        if (noNewNode == 1):
            self.patterns.append(list(visit))


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
                    self.map_info[int(temp[0])] = str(msg[0])+":"+str(msg[1])+":"+str(msg[2])+":"+str(msg[3][:-1])

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
        else:
            print("End events specified by the user: ", self.end_event)

        return self.map_info

    # map_function('large.msg')
    def edge_info(self,file):
        # global bin_edge, old_graph
        with open(file,'r') as f:
            for line in f:
                for elt in line.split(']'):
                    num = [int(s) for s in re.findall(r'-?\d+\.?\d*', elt)]
                    if(len(num)>=3):
                        self.edges[(num[0],num[1])] = num[2]

        self.bin_edge = self.edges.keys()
        self.bin_edge = list(self.bin_edge)

        self.old_graph = self.causlity_graph(self.bin_edge)


    def draw_states(self):
        # targets = list(map_info.keys())
        # print(targets)

        # global patterns, visit
        node_list = self.start_event
        if node_list:
            print("Starting events:", node_list)
            print("Terminating events:", self.end_event)
        else:
            print("Start message is not specified by the user or using # in the message definition file")
            return
        if self.global_depth == 999:
            print("Traverse depth is not specified")
        else:
            print("Traverse depth:", self.global_depth)

        for node in node_list:
            self.patterns = []
            for rule in self.bin_edge:
                if (rule[0] in [node]):  # and src == dest:
                    self.visit.append(rule[0])
                    self.visit.append(rule[1])
                    self.Traverse(root=rule[1], depth=2, visit=self.visit, grow=self.bin_edge)
                    self.visit.remove(rule[1])
                    self.visit.remove(rule[0])

            # print(len(self.patterns))
            src_edges = []

            for path in self.patterns:
                # print(path) #print path of the respective edge
                for i in range(len(path) - 1):
                    temp = path[i], path[i + 1]
                    if temp not in src_edges:
                        src_edges.append(temp)
                        # stock.append(temp)
            src_edges.sort()
            # print(len(src_edges), src_edges)

            new_graph = self.causlity_graph(src_edges)

            # print(new_graph)

            for key in new_graph:
                if self.old_graph[key] == new_graph[key]:
                    pass
                else:
                    old_childs = self.old_graph[key]
                    parents = []
                    for pat in self.patterns:
                        if key in pat:
                            ind = pat.index(key)
                            parents.append(pat[:ind])

                    parents = functools.reduce(operator.iconcat, parents, [])
                    parents = list(set(parents))
                    # print(key, parents)

                    for oc in old_childs:
                        if oc in parents and (key, oc) not in src_edges:
                            # print(key, oc)
                            src_edges.append((key, oc))

            file = "seq_"+str(node)+".txt"

            print("Working for start node ", node)
            descriptor = [] # keeps track if descriptor event is already taken into account

            with open(file,'w') as f:
                if len(src_edges):
                    f.write("@startuml \nhide empty description\n")
                    f.write("[*] -->" +str(src_edges[0][0])+"\n")
                    for i in src_edges:
                        f.write(str(i[0]) + " --> " +str(i[1])+" : "+str(self.edges[tuple(i)])+"\n")
                        descriptor.append(i[0])
                        descriptor.append(i[1])

                    for ev in set(descriptor):
                        f.write(str(ev) + ":" + str(self.map_info[ev]) + "\n")
                    f.write(str(src_edges[-1][1])+" --> [*]\n")
                    f.write("@enduml")
                    f.close()

                    os.system("java -jar plantuml.jar "+file)
                    print(f"Done! State diagram in seq_{node}.png")
                    # try:
                    #     os.remove(file)
                    # except OSError as e:
                    #     print("Error: %s - %s." % (e.file, e.strerror))
                else:
                    print("No DAG found for the current node:", node)


    def draw(self):
        if os.path.isfile(self.msg_file):
            self.map_function(self.msg_file)
        else:
            print("Msg file not found, runing with example file: large.msg")
            self.map_function("large.msg")

        if os.path.isfile(self.support_file):
            self.edge_info(self.support_file)
        else:
            print("Edge support file not found, runing with sol.txt")
            self.edge_info("sol.txt")
        self.draw_states()




#importing example

# pt = Planter()
# pt.start_event = [0] #specify a list of starting messages or specify the starting messages in the msg definition file
# pt.end_event = [25] #specify a list of terminal messages (optional)
# pt.global_depth = 5 #specify a max_height of the path (optional)
# pt.msg_file = 'def.msg' #specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
# pt.support_file = 'supp.txt'# specify the edge support file (default is sol.txt), it is list of edge info in the form [xA_B, number], [xB_C, number], ...
# pt.draw() #call the api