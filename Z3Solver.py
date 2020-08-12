from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from ordered_set import OrderedSet
from py4j.java_gateway import JavaGateway
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from z3 import *

#This function prepares the variables and constraints necessary to run a CSPSolver
#on an annotated acyclic dependency graph
def SearchForAllSolutionsSampleSat():
    # Creates the model.

    s = Solver()

    charID = 'a'
    listOfEdgeVars = []
    listOfNodeVars = []

    print("Generate DAG vars and constraints")
    for dag in dags:

        nodes = dag.getNodes()
        edgeVars = []
        nodeVars = []

        #print("This loop prepares node variables, edge variables, and also all constraints related to the outgoing edges of each node i")
        for i, origin in enumerate(nodes) : 
            nodeIntVar = Int(charID + str(origin.getSymbolIndex()))
            s.add(nodeIntVar == origin.getSupport()) if graph.isRoot(origin) else s.add(nodeIntVar <= origin.getSupport(), 0 <= nodeIntVar)
            nodeVars.append(nodeIntVar)
            edges = origin.getEdges()
            col = []

            if edges.size() != 0 :
                for j, edge in enumerate(edges):
                    edgeSupport = edge.getEdgeSupport()
                    edgeId = charID + str(edge.getId())
                    edgeIntVar = Int(edgeId)
                    s.add(edgeIntVar <= edgeSupport, 0 <= edgeIntVar)
                    col.append(edgeIntVar)

            edgeVars.append(col)
            
            sumIntVars = 0
            if edgeVars[i]:
                for j in range(len(edgeVars[i])) :
                    sumIntVars += edgeVars[i][j]
                #print(sumIntVars, nodeVars[i])
                s.add(nodeVars[i] == sumIntVars)
        
        #print("This loop prepares constraints for every node i that has incoming edges")
        for i, destination in enumerate(nodes) :
            sumIntVars = 0;
            hasSum = False;

            for j, origin in enumerate(nodes) :

                if origin == destination :
                    continue

                edgeID = str(origin.getSymbolIndex()) + '_' + str(destination.getSymbolIndex())
                edges = origin.getEdges()

                if edges.isEmpty() :
                    continue

                for k, edge in enumerate(edges) :
                    if edgeID == edge.getId() :
                        edgeSupport = edge.getEdgeSupport()
                        if edgeSupport != 0 :
                            sumIntVars += edgeVars[j][k] #The sum of all incoming edges to the node at j
                            hasSum = True
            if hasSum:
                #print(sumIntVars, nodeVars[i])
                s.add(nodeVars[i] == sumIntVars)

        charID = chr(ord(charID)+1)
        listOfEdgeVars.append(edgeVars)
        listOfNodeVars.append(nodeVars)
    
    print('Additional constraints created for DAGs, identical nodes across DAGs must have supports that sum up to the total node support of original graph\'s node')
    for node in graph.getNodes():
        
        if graph.isRoot(node):
            continue

        sumIntVars = 0

        for nodeVars in listOfNodeVars :
            for nodeVar in nodeVars :
                if node.getSymbolIndex() in str(nodeVar) :
                    if node.getSymbolIndex() != str(nodeVar)[1:] :
                        continue
                    sumIntVars += nodeVar
            #print(sumIntVars, node.getSymbolIndex())
        if str(sumIntVars) != "0":
            s.add(sumIntVars == node.getSupport())
    
    print('Additional constraints created for DAGs, identical edges across DAGs must have supports that sum up to the total edge support of original graph\'s edge')
    #may need to add additional check related to edges not found in dags? shouldnt be there though
    for edge in graph.getEdges() :

        sumIntVars = 0

        for edgeVars in listOfEdgeVars :
            for edges in edgeVars :
                for edgeVar in edges :
                    if edge.getId() in str(edgeVar) :
                        if edge.getId() != str(edgeVar)[1:] :
                            continue
                        sumIntVars += edgeVar
                        
        if str(sumIntVars) != "0":
            s.add(sumIntVars <= edge.getEdgeSupport(), sumIntVars >= 0)
    
    finalEdges = []

    #print("Convert 2D array of constraints to 1D for Z3Solver")

    for edgeVars in listOfEdgeVars :
        for i in range(len(edgeVars)) :
            #print(edgeVars[i])
            for j in range(len(edgeVars[i])) :
                finalEdges.append(edgeVars[i][j])
    
    print("Check the model")
    
    print(s.to_smt2())
    print(s.check())
      
    old_m = s.model()
   
    constantEdgeVars = finalEdges.copy()
    count = 0

    #print("Beginning solution printing")
    f = open("results.txt", "w")

    while s.check() == sat:
        m = s.model()
        for x in finalEdges:
            if str(m[x]) != '0':
                print(str(x) + " = " + str(m[x]), file=f)
        print("----", file=f)

        count += 1

        for edge in constantEdgeVars:
            if str(old_m[edge]) != str(m[edge]):
                constantEdgeVars.remove(edge)
        
        if not constantEdgeVars:
            break

        for i, dagEdges in enumerate(listOfEdgeVars):
            s.add(Or([ And(old_m[x] == m[x], x != m[x]) for x in constantEdgeVars ]))

    print("Total Solutions: ", count)
    f.close()

#Connects to GatewayServer running in Main.java
gateway = JavaGateway()

print('The definition file being used is ' + str(gateway.entry_point.getDefFileName()))
print('The trace file being used is ' + str(gateway.entry_point.getTraceFileName()))
print()
print('Z3Solver is now running')
print()

count = 1
boolVars = []
listOfConstraintsToBeAdded = []
solutions = []

#Run each trace through the CSP solver until there are no more left in stack
while bool(gateway.entry_point.hasTraces()) :
    print('Analyzing Trace ' + str(count) + ' Solutions\n')
    gateway.entry_point.annotateGraph()
    graph = gateway.entry_point.getGraph()
    nodes = graph.getNodes()
    dags = gateway.entry_point.getAnnotatedDAGS()
    #graph.detectAndRemoveCycle()
    SearchForAllSolutionsSampleSat()
    graph.resetGraphSupport()
    print()
    print('End of Trace ' + str(count) + ' Solutions\n')
    count += 1
    gateway.entry_point.popTrace()
    
print()
print('All traces have been analyzed. Please re-run Main.java to perform experiments again.')

       




