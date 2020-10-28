Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. graphviz (for mac: brew install graphviz, for linux: sudo apt install graphviz)
3. plantuml.jar (I have shipped it already or download from: https://plantuml.com/starting)
4. java (should be available in mac, or download from: https://www.java.com/en/download/)
(2,3,4 are plantUML depenencies)

## How to run:
1. Go to visualization directory
2. type ``` python3 demo.py```
3. See simple output in ```tests``` folder
4. If there is a error, unable to print uml, then make sure ```seq{time-st-amp}.txt``` and ```plantuml.jar``` are in the consistent location as described in line 163 of 
```planterUML.py```
5. Enter prefix seperated by spaced only, for example '0 18 10 11' with no ''.
6. Use no details to caputure large graph, details tends to be cut off.
7. Output files i. a text file, and ii. a png file will be placed in the same folder

## demo.py content
```
demo.py
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
pt.prefix = prefix

#following two lines can be commented out, and then deafult large.msg and sol-sequences.txt will be used (these files can be found in the src folder)
pt.msg_file = './src/large.msg' # specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
pt.sol_file = './src/sol-sequences.txt'# specify the solution file

# pt.draw(detailed=0) #call the api, detailed = 1 means nodes complete definition, if detailed = 0(which is default), only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.
pt.draw(detail_level)
```
