import networkx as nx 
import matplotlib.pyplot as plt
import numpy as np
import sys
import joblib
from datetime import datetime
import scipy as sp

class optimizedEvaluation:
	def __init__(self, traceFilePath, causalityGraphG, resultFileName):
		self.G = causalityGraphG #nx.DiGraph()
		self.sizeOfAdMatrix = 100 #8
		self.adMatrix = [[0 for x in range(self.sizeOfAdMatrix)] for y in range(self.sizeOfAdMatrix)] 
		self.FSMadMatrix = [[0 for x in range(self.sizeOfAdMatrix)] for y in range(self.sizeOfAdMatrix)]
		self.arrayOfActivePaths = [0] * self.sizeOfAdMatrix
		self.toBePrinted = ""
		self.maxIndexNode = 0
		self.tracesArray = []
		self.fileName = resultFileName
		self.traceFilePath = traceFilePath

	# def read_causality_graph(self, path):
	# 	global maxIndexNode, G
	# 	try:
	# 		with open(path, 'r') as File:
	# 			infoFile = File.readlines() 
	# 			eachFile = []
	# 			for line in infoFile: 
	# 				words = line.split(" ")
	# 				G.add_edge(int(words[0]), int(words[1]))
	# 				adMatrix[int(words[0])][int(words[1])] = 1
	# 				if (maxIndexNode < int(words[0])):
	# 					maxIndexNode = int(words[0])
	# 				if (maxIndexNode < int(words[1])):
	# 					maxIndexNode = int(words[1])
	
	# 		print ("\tMaximum number of nodes is : ", maxIndexNode)

	# 	except FileNotFoundError as e:
	# 		print ("\tError Reading Solution File!")
	# 		exit()


	def read_synthetic_traces(self, path):
		# global tracesArray
		tempTraceArray = []
		flag = False
		try:
			with open(path, 'r') as File:
				infoFile = File.readlines() 
				eachFile = []
				for line in infoFile: 
					words = line.split(" ")
					for i in words:
						# print (i)
						if (i != '' and i != '\n' and i != '-1' and i != '-2'):
							flag = True
							# print (i)
							tempTraceArray.append(int(i))
						elif (i == '-2'):
							flag = False
							# print (i)
							self.tracesArray.append(tempTraceArray)
							tempTraceArray = []
					if flag == True:
						self.tracesArray.append(tempTraceArray)
						tempTraceArray = []
		except FileNotFoundError as e:
			print ("\tError Reading Traces File!")
			exit()

	def read_jbl_traces (self, path):
		file = joblib.load(path)

		for i, j in enumerate(file):
			tempTrace = []
			for each in file[j]:
				tempTrace.append(int(each))
			self.tracesArray.append(tempTrace)
		

	def read_inputs(self, traceFilePath):
		# read_causality_graph(causalityGraphFilePath)
		trace_file_type = traceFilePath.split('.')
		if trace_file_type[-1] == "txt":
			self.read_synthetic_traces(traceFilePath)
		else:
			self.read_jbl_traces(traceFilePath)


	def write_to_file (self, fileName, writeString):
		with open(fileName, 'a') as f:
	    		f.write(writeString)


	def find_path (self, inputTrace):

		toBeremoved = 0
		totalNumberOfEvents = 0
		self.arrayOfActivePaths = [0] * self.sizeOfAdMatrix
		checkFlag = False
		ratio = 0
		numberofRatios = 0
		
		for i in inputTrace:
			totalNumberOfEvents += 1
			checkFlag = False
		
			if self.FSMadMatrix[-1][i] == 1:
				self.arrayOfActivePaths[i] += 1
				checkFlag = True
				
			if checkFlag == False:
				for op in range(self.sizeOfAdMatrix-1):
					if (self.FSMadMatrix[op][i] == 1 and self.arrayOfActivePaths[op] > 0 and checkFlag == False):
						self.arrayOfActivePaths[op] -= 1
						self.arrayOfActivePaths[i]  += 1
						checkFlag = True
						break
						
			if checkFlag == False:
				# print ("First unaccepted = ", i)
				# exit()
				toBeremoved += 1
		
		self.toBePrinted += "\n\tTotal number of events is equal to " + str(totalNumberOfEvents) + "\n\tTotal number of unaccepted events is equal to " + str(toBeremoved)
		print ("\tTotal number of events is equal to ", totalNumberOfEvents)
		print ("\tTotal number of unaccepted events is equal to ", toBeremoved)
			
		
		unfinishedEvents = 0
		numberOfUnfinishedTraces = 0
		
		for aNode in self.G:
			if (self.G.out_degree(aNode) == 0):
				self.arrayOfActivePaths[int(aNode)] = 0
		for i in range(self.sizeOfAdMatrix-1):
			if self.arrayOfActivePaths[i] > 0 :
				numberOfUnfinishedTraces += 1
				unfinishedEvents += self.arrayOfActivePaths[i]
		
		# ratio = ((totalNumberOfEvents - toBeremoved - unfinishedEvents)/totalNumberOfEvents)  # considering unfinished traces
		ratio = ((totalNumberOfEvents - toBeremoved)/totalNumberOfEvents) # without considering unfinished traces
		
		# self.toBePrinted += "\n\tTotal number of unaccepted traces = " + str(numberOfUnfinishedTraces)
		# self.toBePrinted += "\n\tTotal number of unfinished events = " + str(unfinishedEvents)
		# self.toBePrinted += "\n\tFinal Acceptance rate for this trace file is equal to " + str((totalNumberOfEvents - toBeremoved - unfinishedEvents)/totalNumberOfEvents)
		# self.toBePrinted += "\tFinal number of unaccepted events is equal to " + str(toBeremoved + unfinishedEvents)
		# print ("\tTotal number of unaccepted traces = ", numberOfUnfinishedTraces)
		# print ("\tTotal number of unfinished events = ", unfinishedEvents)
		# print ("\tFinal Acceptance rate for this trace file is equal to ", ((totalNumberOfEvents - toBeremoved - unfinishedEvents)/totalNumberOfEvents))
		# print ("\tFinal number of unaccepted events is equal to ", (toBeremoved + unfinishedEvents))
		
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		self.toBePrinted += "\n\tCurrent Time =" + current_time + "\n"
		print("\tCurrent Time =", current_time)
		print ("\n")

		return ratio, totalNumberOfEvents, (totalNumberOfEvents - toBeremoved)



	def evaluate(self):
		##################################################################################### Main #####################################################################################
		# G = causalityGraphG

		# modelName = sys.argv[1].split('/')
		# fileName = "output/" + sys.argv[3] + modelName[3] + "_" + modelName[4] + "_" + modelName[1] + "_" + modelName[5]
		# fileName = "./evaluationResults/" + sys.argv[3] + "_" + modelName[1] + "_" + sys.argv[2].split('/')[1]
		# fileName = resultFileName
		# print ("FilrName = ", fileName)
		# exit()


		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		self.toBePrinted += "\nStart Time =" + current_time
		print("\nStart Time =", current_time)

		self.read_inputs(self.traceFilePath)

		self.toBePrinted += "\n\t------------------------------------------------------------------Creating the Finite State Machine------------------------------------------------------------------"
		print ("\t------------------------------------------------------------------Creating the Finite State Machine------------------------------------------------------------------")


		############################################ Uncomment for Synoptic and texada solutions (Start)
		# print ("Start event = ", tracesArray[0])
		# print ("End event = ", tracesArray[-1])
		# FSMadMatrix[-1][tracesArray[0]] = 1
		# FSMadMatrix[tracesArray[-1]][-1] = 1
		############################################ Uncomment for Synoptic and texada solutions (End)

		for aNode in self.G:
			if (self.G.in_degree(aNode) == 0):
				self.FSMadMatrix[-1][int(aNode)] = 1
				# print ("Start event = ", int(aNode))

				for n in self.G.neighbors(aNode):
					self.FSMadMatrix[int(aNode)][int(n)] = 1
			else:
				for n in self.G.neighbors(aNode):
					self.FSMadMatrix[int(aNode)][int(n)] = 1

			if (self.G.out_degree(aNode) == 0):
				self.FSMadMatrix[int(aNode)][-1] = 1
				# print ("End event = ", int(aNode))

		self.toBePrinted += "\n\tDone creating the Finite State Machine!"
		# self.toBePrinted += "\n\t----------------------------------------------------------------From now on we are testing the parser----------------------------------------------------------------"
		print ("\tDone creating the Finite State Machine!")
		# print ("\t----------------------------------------------------------------From now on we are testing the parser----------------------------------------------------------------")


		finalRatio = 0
		finalNumberofRatios = 0
		totalCountOfEvents = 0
		finalTotalAccepted = 0


		print ("\n")
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		print("\tCurrent Time =", current_time)
		self.toBePrinted += "\n\n\tCurrent Time =" + current_time


		for traceIndex in range(len(self.tracesArray)):

			############################################ Uncomment for Synoptic and texada solutions (Start)
			# FSMadMatrix[-1][tracesArray[traceIndex][0]]  = 1
			# FSMadMatrix[tracesArray[traceIndex][-1]][-1] = 1
			############################################ Uncomment for Synoptic and texada solutions (End)

			self.toBePrinted += "\n\tTrace number " + str(traceIndex) + " : "
			print ("\tTrace number ", traceIndex, " : ")
			R, TNOfE, totalAccepted = self.find_path(self.tracesArray[traceIndex])

			finalTotalAccepted += totalAccepted
			finalRatio += R
			finalNumberofRatios += 1
			totalCountOfEvents += TNOfE

			############################################ Uncomment for Synoptic and texada solutions (Start)
			# FSMadMatrix[-1][tracesArray[traceIndex][0]]  = 0
			# FSMadMatrix[tracesArray[traceIndex][-1]][-1] = 0
			############################################ Uncomment for Synoptic and texada solutions (End)

			
			############################################ Uncomment for Synoptic and texada solutions (Start)
			# FSMadMatrix[-1][tracesArray[0]]  = 1
			# FSMadMatrix[tracesArray[-1]][-1] = 1
			############################################ Uncomment for Synoptic and texada solutions (End)


		self.toBePrinted += "\n\tTotal number of events = " + str(totalCountOfEvents)
		self.toBePrinted += "\n\tNumber of traces = " + str(finalNumberofRatios)
		self.toBePrinted += "\n\tThe final answer (ratios/total) is : " + str(finalRatio/finalNumberofRatios)
		self.toBePrinted += "\n\tThe final answer (# of accepted events/total # of events) is : " + str(finalTotalAccepted/totalCountOfEvents)
		print ("\tTotal number of events = ", totalCountOfEvents)
		print ("\tNumber of traces = ", finalNumberofRatios)
		print ("\tThe final answer (ratio/total) is : ", (finalRatio/finalNumberofRatios) )
		print ("\tThe final answer (# of accepted events/total # of events) is : ", (finalTotalAccepted/totalCountOfEvents) )


		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		print("\nEnd Time =", current_time)
		print ("")
		self.toBePrinted += "\n\nEnd Time =" + current_time + "\n\n\n\n\n"

		FSMSize = 0
		for i in range(self.sizeOfAdMatrix):
			for j in range(self.sizeOfAdMatrix):
					if self.FSMadMatrix[i][j] == 1:
						FSMSize += 1
		print ("FSM Size (edges in FSM) = ", FSMSize)
		print ("Size (edges causality graph) = ", self.G.number_of_edges())
		print ("FSM Size (nodes) = ", self.G.number_of_nodes())
		self.toBePrinted += "\n FSM Size (edges in FSM) = " + str(FSMSize) 
		self.toBePrinted += "\n Size (edges causality graph) =" + str(self.G.number_of_edges()) 
		self.toBePrinted += "\n FSM Size (nodes) =" + str(self.G.number_of_nodes()) + "\n\n\n\n\n\n\n\n"

		self.write_to_file(self.fileName, self.toBePrinted)

		return (finalRatio/finalNumberofRatios), (finalTotalAccepted/totalCountOfEvents)


