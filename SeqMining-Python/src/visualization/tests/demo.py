from src.planterUML import Planter

pt = Planter()
pt.prefix = [0, 18, 10, 11] # specify the prefix for which UML will be drawn (has default [0, 18, 10])
#following two lines can be commented out, and then deafult large.msg and sol-sequences.txt will be used (these files can be found in the src folder)
pt.msg_file = 'def.msg' # specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
pt.sol_file = 'sol.txt'# specify the solution file
pt.draw(detailed=0) #call the api, detailed = 1 means nodes complete definition, if detailed = 0(which is default), only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.
