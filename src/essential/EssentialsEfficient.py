import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import sys
import joblib
import scipy as sp
from datetime import datetime


sizeOfMatrix = 100 #8
MessageDefinitionArray = [[0 for x in range(5)] for y in range(sizeOfMatrix)] 

tracesArray = []
forwardEssentialFinderArray  = [0 for x in range(sizeOfMatrix)] 
backwardEssentialFinderArray = [0 for x in range(sizeOfMatrix)] 
forwardEssentialCausalityMatrix  = [[0 for x in range(sizeOfMatrix)] for y in range(sizeOfMatrix)] 
backwardEssentialCausalityMatrix = [[0 for x in range(sizeOfMatrix)] for y in range(sizeOfMatrix)] 
forwardAndBackwardEssentialCausalitiesTogether = [[0 for x in range(sizeOfMatrix)] for y in range(sizeOfMatrix)] 

# print ("Essential Causality Finder Program")

def read_message_definition_file (path):
	global maxIndexNode, G
	headTailIndicator = "startLine"
	try:
		with open(path, 'r') as File:
			infoFile = File.readlines() 
			for line in infoFile: 
				line = line.replace(" ", "")
				line = line.replace("\n", "")
				if (line != "#"): #line != "\n" and 
					words = line.split(":")
					MessageDefinitionArray[int(words[0])][0] = words[1]
					MessageDefinitionArray[int(words[0])][1] = words[2]
					MessageDefinitionArray[int(words[0])][2] = words[3]
					if words[4] == "req\n":
						MessageDefinitionArray[int(words[0])][3] = "req"
					elif words[4] == "resp\n":
						MessageDefinitionArray[int(words[0])][3] = "resp"
					else:
						MessageDefinitionArray[int(words[0])][3] = words[4]

					MessageDefinitionArray[int(words[0])][4] = headTailIndicator
				else:
					if headTailIndicator == "startLine":
						headTailIndicator = "head"
					elif headTailIndicator == "head":
						headTailIndicator = "body"
					elif headTailIndicator == "body":
						headTailIndicator = "tail"
					else:
						headTailIndicator = "finished"

	except FileNotFoundError as e:
		print ("\tError Reading Message Definition File!")
		exit()



def read_synthetic_traces(path):
	global tracesArray
	tempTraceArray = []
	checkAddedFlag = 0
	try:
		with open(path, 'r') as File:
			infoFile = File.readlines() 
			# eachFile = []
			for line in infoFile: 
				words = line.split(" ")
				for i in words:
					if (i != '' and i != '\n' and i != '-1' and i != '-2'):
						tempTraceArray.append(int(i))
					elif (i == '-2'):
						checkAddedFlag += 1
						tracesArray.append(tempTraceArray)
						tempTraceArray = []

			if checkAddedFlag == 0:
				checkAddedFlag += 1
				tracesArray.append(tempTraceArray)
				tempTraceArray = []

	except FileNotFoundError as e:
		print ("\tError Reading Traces File!")
		exit()

def read_jbl_traces (path):
	file = joblib.load(path)

	for i, j in enumerate(file):
		tempTrace = []
		for each in file[j]:
			tempTrace.append(int(each))
		tracesArray.append(tempTrace)


def find_essential_causalities(message_definition_file_path, trace_file_path):
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	# print("\tCurrent Time =", current_time)
	# print ("\n")
	
	read_message_definition_file(message_definition_file_path)  
	# print (trace_file_path) 
	trace_file_type = trace_file_path.split(".")
	if trace_file_type[-1] == "txt":   
		read_synthetic_traces(trace_file_path)
	else:
		read_jbl_traces(trace_file_path)

	
	totalSize = 0
	maxIndex  = 0
	for eachTrace in tracesArray:
		# print ("test!")
		totalSize += len(eachTrace)
		for anEvent in eachTrace:
			if maxIndex < anEvent:
				maxIndex = anEvent
	# print ("Input size = ", totalSize)
	# print ("Max Index  = ", maxIndex)
	
	
	###################################################### Forward
	for eachTrace in tracesArray:
		for anEvent in eachTrace:
			forwardEssentialFinderArray[anEvent] += 1
			foundFlag = False
			foundIndex = -1
			contradictionFlag = False
			for previousEventsIndex in range(sizeOfMatrix):
				if (forwardEssentialFinderArray[previousEventsIndex] != 0):
					if  (MessageDefinitionArray[anEvent][0] == MessageDefinitionArray[previousEventsIndex][1] and MessageDefinitionArray[anEvent][4] != "head"):
						if (MessageDefinitionArray[anEvent][4] != "body" or MessageDefinitionArray[previousEventsIndex][4] != "body") or MessageDefinitionArray[anEvent][3] != MessageDefinitionArray[previousEventsIndex][3]:
							if foundFlag == False:
								foundFlag = True
								foundIndex = previousEventsIndex
							else:
								if foundIndex != previousEventsIndex:
									contradictionFlag = True
					if contradictionFlag == True:
							break
			if (contradictionFlag == False and foundFlag == True):
				forwardEssentialCausalityMatrix[foundIndex][anEvent] = 1
				forwardAndBackwardEssentialCausalitiesTogether[foundIndex][anEvent] = 1
				forwardEssentialFinderArray[foundIndex] -= 1
	
	
	
	###################################################### Backward
	for eachTrace in tracesArray:
		for anEvent in reversed(eachTrace):
			backwardEssentialFinderArray[anEvent] += 1
			foundFlag = False
			foundIndex = -1
			contradictionFlag = False
			for nextEventsIndex in range(sizeOfMatrix):
				if (backwardEssentialFinderArray[nextEventsIndex] != 0):
					if  (MessageDefinitionArray[anEvent][1] == MessageDefinitionArray[nextEventsIndex][0] and MessageDefinitionArray[anEvent][4] != "tail"):
						if ((MessageDefinitionArray[anEvent][4] != "body" or MessageDefinitionArray[nextEventsIndex][4] != "body") or MessageDefinitionArray[anEvent][3] != MessageDefinitionArray[nextEventsIndex][3]) or ((MessageDefinitionArray[anEvent][4] == "body" and MessageDefinitionArray[nextEventsIndex][4] == "body") and MessageDefinitionArray[anEvent][0] != MessageDefinitionArray[nextEventsIndex][1]) or ((MessageDefinitionArray[anEvent][4] == "body" and MessageDefinitionArray[nextEventsIndex][4] == "body") and (MessageDefinitionArray[anEvent][0] == MessageDefinitionArray[nextEventsIndex][1]) and (MessageDefinitionArray[anEvent][3] != MessageDefinitionArray[nextEventsIndex][3])) :
							if foundFlag == False:
								foundFlag = True
								foundIndex = nextEventsIndex
							else:
								if foundIndex != nextEventsIndex:
									contradictionFlag = True
					if contradictionFlag == True:
						break
			if (contradictionFlag == False and foundFlag == True):
				backwardEssentialCausalityMatrix[anEvent][foundIndex] = 1
				forwardAndBackwardEssentialCausalitiesTogether[anEvent][foundIndex] = 1

	
	
	# print ("\nEssential Causalities found (Forward):")
	# for i in range(sizeOfMatrix):
	# 	for j in range(sizeOfMatrix):
	# 		if forwardEssentialCausalityMatrix[i][j] == 1:
	# 			print ("\t", i, " -> ", j)
	
	
	# print ("\nEssential Causalities found (Backward):")
	# for i in range(sizeOfMatrix):
	# 	for j in range(sizeOfMatrix):
	# 		if backwardEssentialCausalityMatrix[i][j] == 1:
	# 			print ("\t", i, " -> ", j)
	
	output_array = []
	# print ("\nEssential Causalities found (All Together):")
	for i in range(sizeOfMatrix):
		for j in range(sizeOfMatrix):
			if forwardAndBackwardEssentialCausalitiesTogether[i][j] == 1:
				output_array.append(str(i)+"_"+str(j))
				# print ("\t", i, " -> ", j)
	
	
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	# print("\tCurrent Time =", current_time)
	# print ("\n")

	return output_array

# find_essential_causalities("src/messageDefinitionFile.txt", "src/traces/synthetic/trace-small-5.txt")
# exit()