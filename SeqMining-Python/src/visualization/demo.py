from plantUML import Planter
#importing example

pt = Planter()
pt.start_event = [0] #specify a list of starting messages or specify the starting messages in the msg definition file
pt.end_event = [25] #specify a list of terminal messages (optional)
pt.global_depth = 5 #specify a max_height of the path (optional)
pt.msg_file = 'def.msg' #specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
pt.support_file = 'supp.txt'# specify the edge support file (default is sol.txt), it is list of edge info in the form [xA_B, number], [xB_C, number], ...
pt.draw() #call the api


# print(pt.global_depth)

class CSStudent():
    stream = 'cse'  # Class Variable
    name = 'Gopal'
    roll = 12

    def draw2(self, st, roll=1000):
        if self.roll > 1000:
            return st + "!!!"
        else:
            return st

    def draw(self):
        print(self.stream)
        print(self.draw2("ass", self.roll))



# std = CSStudent()
# std.draw()


# Objects of CSStudent class
# a = CSStudent('Geek', 1, 'SW')
# b = CSStudent('Nerd', 2, 'ME')
# c = CSStudent("gp", 12)
# CSStudent.roll = 20
# c.draw()

# Class variables can be accessed using class
# name also
# print(CSStudent.roll)  # prints "cse"


# import networkx as nx
graph = {0: [1], 1: [2, 3], 2: [1], 3:[0]}
# G = nx.DiGraph(graph)

def find_all_paths(graph, start, end, path=[]):
    path = path + [start]
    if start == end or len(path) == 4:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)
    return paths

# print(find_all_paths(graph, 0, 4))

# for path in nx.all_simple_paths(G, source=0, target=[1,2,3,4]):
#     print(path)

dictA = {0: [1], 1: [2, 3], 2: [], 3:[]}

def GetKey(val, dt):
    parents = []
    for key, value in dt.items():
        if val in value:
            parents.append(key)
    if parents:
        return parents
    else:
        return ""

# print(GetKey(0))

# for key in dictA:
#     if graph[key] == dictA[key]:
#         print(key)
#     else:
#         # old_parents = GetKey(key, graph)
#         # new_parents = GetKey(key, dictA)
#         old_childs = graph[key]
#         for oc in old_childs:
#             if oc in dictA.keys():
#                 print(key,oc)
#
# a = [(1,3), (2,3), (4, 2)]
# b = []
#
# for i, j in a:
#     b.append(i)
#     b.append(j)
#
# b = set(b)
# b = list(b)
# b.sort()
# print(b)
