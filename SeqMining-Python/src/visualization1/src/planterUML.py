import re, os, random, sys
from datetime import datetime
from uml_graph import *

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
                    # print(temp)
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
        print(f'{len(self.patterns)} sequences found for the given prefix.')
        for k, pat in enumerate(self.patterns):
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
            file_str = "seq"+now.strftime("%H-%M-%S")
            out_file = file_str+".txt"
            with open(out_file, 'w') as f:
                f.write("@startuml \nhide empty description\n")
                f.write("[*] -->" + str(edges[0][0]) + "\n")
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

                        f.write(str(i[0]) + " --> " + str(i[1]) + " : " + str(self.CG[i[0]][1])+":" + str(self.map_info[self.CG[i[0]][1]][2]) + "\n")
                        if self.CG[i[1]][1] in self.end_event:
                            rand_end = self.rn()
                            end_ev = "end"+str(rand_end)
                            f.write(str(i[1]) + " --> " + end_ev + " : " + str(self.CG[i[1]][1]) + ":" + str(self.map_info[self.CG[i[1]][1]][2]) + "\n")
                            descriptor.append(end_ev)
                            # print(self.map_info[self.CG[i[1]][1]])
                            self.map_info[end_ev] = self.map_info[self.CG[i[1]][1]]

                        descriptor.append(i[0])
                        descriptor.append(i[1])
                    else:
                        f.write(str(i[0]) + " --> " + str(i[1]) + " : " + "x" + "\n")
                        descriptor.append(i[0])
                        descriptor.append(i[1])


                for ev in set(descriptor):
                    if detailed:
                        if 'end' in str(ev):
                            f.write(str(ev) + ":" + str(self.map_info[ev][1]) + "\n")
                        else:
                            f.write(str(ev) + ":" + str(self.map_info[self.CG[ev][1]][0]) + "\n")
                    else:
                        f.write(str(ev) + ":" + str(self.CG[ev][1]) + "\n")

                f.write(str(edges[-1][1]) + " --> [*]\n")
                f.write("@enduml")
                f.close()
                # print(sys.path[1])
                os.system("java -jar "+ str(sys.path[1])+"/plantuml.jar " + out_file)
                print(f"Done! State diagram @{file_str}.png")
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


# pt = Planter()
# pt.prefix = [0, 18, 10, 11]
# pt.msg_file = 'def.msg' #specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
# pt.sol_file = 'supp.txt'# specify the solution file (default is sol-sequences.txt)
# pt.draw(detailed=1) #call the api, detailed = 1 means nodes complete definition, if detailed = 0, only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.