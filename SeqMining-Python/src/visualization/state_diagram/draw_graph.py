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
	map_info = {}

	start_event = []

	end_event = []

	prev_random = []

	edges = []

	processed_verts = []

	leaves = []

	node_connections = {} # {node:[parents], [children]}


	def rn(self):
		# global prev_random

		while True:
			rand = random.randint(0,2000)

			if rand not in self.prev_random:
				self.prev_random.append(rand)
				return rand
		return -1

	def parse_seqs(self, file):
	    seqs = open(file).read()
	    new_str = re.sub('[^a-zA-Z0-9\n\.]', ' ', seqs)
	    open('b.txt', 'w').write(new_str)

	    # patterns = []
	    with open('b.txt', "r", encoding='utf-8-sig') as f:
	        lines = [line.strip() for line in f.readlines()]
	        for line in lines:
	            temp = (line.split(" "))
	            temp = [int(i) for i in temp if len(i)]
	            self.edges.append(temp)
	            # if temp[0:len(self.prefix)] == self.prefix:# and temp[-1] in self.end_event:
	            #     if self.end_event:
	            #         if temp[-1] in self.end_event:
	            #             self.patterns.append(temp)
	            #     else:
	            #         self.patterns.append(temp)
	    os.remove('b.txt')
	#     return -1

	def map_function(self,file):
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

	        # if len(start_ends)>=2:
	        #     start_events = lines[start_ends[0]:start_ends[1]]
	        # if len(start_ends)>=4:
	        #     end_events = lines[start_ends[2]:start_ends[3]]

	        # if len(start_event) == 0:
	        #     for line in start_events:
	        #         if line == "#\n" or line == "#":
	        #             pass
	        #         else:
	        #             temp = line.split(":")
	        #             start_event.append(int(temp[0]))
	        # else:
	        #     print("Start events specified by the user: ", start_event)

	        # if len(end_event) == 0:
	        #     for line in end_events:
	        #         if line == "#\n" or line == "#":
	        #             pass
	        #         else:
	        #             temp = line.split(":")
	        #             end_event.append(int(temp[0]))
	        #     print("End events specified by the user: ", end_event)
	        # else:
	        #     print("End events specified by the user: ", end_event)

	        # return map_info

	def node_connections_finder(self):
		nodes = sum(self.edges,[])
		nodes = list(set(nodes))

		for node in nodes:
			parents = []
			children = []
			for edge in self.edges:
				if edge[0] == node:
					children.append(edge[1])
				elif edge[1] ==node:
					parents.append(edge[0])
				else:
					pass

			self.node_connections[node] = [parents, children]

		for node in self.node_connections: # connecting terminal nodes to roots.
			if self.node_connections[node][1] == []:
				for par in self.node_connections[node][0]:
					if self.map_info[par][0] == self.map_info[node][1]:
						self.edges.append([node,par])
						# print([node,par])

		# print(self.node_connctions)	


	def edge_to_graph(self):
		# nodes = sum(self.edges,[])
		# nodes = list(set(nodes))
		self.node_connections_finder()

		g = Graph()

		# print(map_info)

		for i in self.edges:
		    if i[0] not in self.processed_verts:
		        g.add_vertex(str(i[0]), self.map_info[i[0]][0])
		        # print(str(i[0]), map_info[i[0]][0])

		    if i[1] not in self.processed_verts: 
		        g.add_vertex(str(i[1]), self.map_info[i[1]][0])
		        # print(str(i[1]), map_info[i[1]][0])

		    g.add_edge(str(i[0]), str(i[1]), self.map_info[i[0]][2])

		    self.processed_verts.append(i[0])
		    self.processed_verts.append(i[1])


		self.leaves = [int(i) for i in g.get_leaves()]

		# for leaf in self.leaves:
		# 	rand_end = self.rn()
		# 	g.add_vertex(str(rand_end), self.map_info[leaf][1])
		# 	g.add_edge(str(leaf), str(rand_end), self.map_info[leaf][2])
		# 	# print(str(leaf), str(rand_end),map_info[leaf][2])

		# 	self.processed_verts.append(rand_end)

		return g

	def graph_pruning(self,g):
		# for node in self.node_connections:
		# 	print(node, self.node_connections[node])

		removable = []

		for v in g:
			# print("\n",v.get_id())
			conns = list(v.get_connections())
			if len(conns)>1:
				siblings_group = [] #children of a vertex, checking if all of them have single root.
				for w in conns:
					if [int(v.get_id())] == self.node_connections[int(w.get_id())][0]: #single parent for all childs
					# if int(v.get_id()) in self.node_connections[int(w.get_id())][0] and self.map_info[int(v.get_id())][1] == self.map_info[int(w.get_id())][0]:

						# g.remove_edge(w.get_id(),v.get_id())
						siblings_group.append(int(w.get_id()))

				if len(siblings_group)>1:
					live_node = siblings_group[0]
					# print("live_node", live_node)

					for sib in siblings_group[1:]:
						for ch in self.node_connections[sib][1]:
							g.add_edge(str(live_node), str(ch), self.map_info[sib][2])
							# print("added:", live_node, str(ch), self.map_info[sib][2])

						g.remove_edge(str(sib), v.get_id())
						removable.append(sib)

		removable = set(removable)
		# print("Removable: ",removable)
		for vert in removable:
			g.remove_vertex(str(vert))
					# print(v.get_id(),siblings_group)
		return g


	def draw(self, msg_file, seq_file):
		self.map_function(msg_file)
		self.parse_seqs(seq_file)
		g = self.edge_to_graph()
		g = self.graph_pruning(g)
		
		cpus = []
		cache0s = []
		cache1s = []
		membuses = []
		mems = []
		periferals = []

		now = datetime.now()

		file_str = "seq-"+now.strftime("%H-%M-%S")
		# file_str = "simple"
		out_file = file_str+".dot"

		components = []

		for v in g:
			node = v.get_id()+"_"+v.label
			components.append(node)
			# print ('\"%s_%s\"' % (v.get_id(), v.label), end="; ")
		# print("\n")
		
		# print(nodes)
		
		with open(out_file, 'w') as f:
			
			f.write("digraph asde91{\n")
			f.write("\n ranksep=.75;\n node [color=red,fontname=Courier,shape=box, weight=.5]\n edge [color=white, style=dashed]\n\n" )

			color = 1

			for node in components:
				if 'cpu' in node:
					cpus.append(node)
				elif 'cache0' in node:
					cache0s.append(node)
				elif 'cache1' in node:
					cache1s.append(node)
				elif 'membus' in node:
					membuses.append(node)
				elif 'mem' in node:
					mems.append(node)
				else:
					periferals.append(node)

			nodes = [cpus, cache0s, cache1s, membuses, mems, periferals]

			f.write("\n{ 1->2->3->4->5->6;\n")
			for node in components:
				f.write("\""+node+"\""+'; ')
			f.write("\n}\n\n")

			for  rank ,node in enumerate(nodes):
				f.write("{ rank=same; "+str(rank+1)+"; ")
				for n in node:
					# print(rank, n, end=" ")
					f.write("\""+n+"\"; ")
				f.write(" }\n")
				# print()
			f.write("\n\n")
			
			f.write("\n node [color=red,fontname=Courier,shape=box, weight=.2]\n edge [color=blue4, fontname=Courier, style=dotted]\n\n" )
			
			for v in g:
				for w in v.get_connections():
				    vl = v.label
				    wl = w.label
				    # print ('%s_%s'  % (w.get_id(), wl), end="; ")

				    if color:
				        color = 0
				        # f.write("{id"+str(v.get_id())+"_"+str(vl)+"[color=red]}\n")
				        # prind"+str(v.get_id())+"_"+str(vl)+"[color=red]}")

				    if w.get_id() not in self.leaves:
				        # print ('id%s_%s->id%s_%s[label=\"%s\"];'  % (v.get_id(), vl, w.get_id(), wl, v.get_weight(w))) #dot format
				        # f.write("id"+str(v.get_id())+"_"+str(vl)+"->id"+str(w.get_id())+"_"+str(wl)+"[label=\""+str(v.get_weight(w))+"\"];\n")
				        f.write("\""+str(v.get_id())+"_"+str(vl)+"\"->\""+str(w.get_id())+"_"+str(wl)+"\""+"[label=\""+str(v.get_weight(w))+"\"];\n") #with ranks

				        # print ('%s_%s --> %s_%s : %s'  % (v.get_id(), vl, w.get_id(), wl, v.get_weight(w))) #plantUML format
				        # print ('\"%s_%s\"->\"%s_%s\"[label=\"%s\"];'  % (v.get_id(), vl, w.get_id(), wl, v.get_weight(w))) #dot format

				    else:
				        # print ('id%s_%s->%s[label=\"%s\"];'  % (v.get_id(), vl, wl, v.get_weight(w))) #dot format
				        # f.write("id"+str(v.get_id())+"_"+str(vl)+"->"+str(wl)+"[label=\""+str(v.get_weight(w))+"\"];\n")
				        f.write("\""+str(v.get_id())+"_"+str(vl)+"->"+str(wl)+"\""+"[label=\""+str(v.get_weight(w))+"\"];\n") #with ranks

				        # print ('id%s_%s->%s[label=\"%s\"];'  % (v.get_id(), vl, wl, v.get_weight(w))) #plantUML format
				        # print(leaves)

				# print ('\"%s_%s\"' % (v.get_id(), v.label), end="; ")

			f.write("}")
		f.close()

		# print(g.get_vertices())
		B = pgv.AGraph(out_file)  # create a new graph from file
		B.layout(prog='dot')  # layout with default (neato)
		B.draw(file_str+".png")  # draw png
		vertices = g.get_vertices()
		print("\nNumber of vertices in the graph: ",len(vertices))
		os.remove(file_str+".dot")
		print("\nWrote "+file_str+".png")



# pt = Planter()

# pt.draw('large.msg','model.txt')
