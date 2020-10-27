from src.planterUML import Planter

prefix_string = input("Prefix for sequences to show(ex: 0 18 10): ")
prefix = []
prefix_string = prefix_string.split()
for e in prefix_string:
    prefix.append(int(e))
print(prefix)


detail_string = 0
detail_string = input('Details in the graphs (0: no message definition, 1: with message definition): ')
detail_level = int(detail_string)

pt = Planter()
# pt.prefix = [0, 18, 10, 11] # specify the prefix for which UML will be drawn (has default [0, 18, 10])
pt.prefix = prefix

#following two lines can be commented out, and then deafult large.msg and sol-sequences.txt will be used (these files can be found in the src folder)
pt.msg_file = './src/large.msg' # specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
pt.sol_file = './src/sol-sequences.txt'# specify the solution file

# pt.draw(detailed=0) #call the api, detailed = 1 means nodes complete definition, if detailed = 0(which is default), only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.
pt.draw(detail_level)