Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. graphviz (for mac: brew install graphviz, for linux: sudo apt install graphviz)
3. plantuml.jar (I have shipped it already or download from: https://plantuml.com/starting)
4. java (should be available in mac, or download from: https://www.java.com/en/download/)
(2,3,4 are plantUML depenencies)

## How to run:
1. Go to visualization directory
2. type ``` python3 demo.py```
3. Output of this demo is kept into ```tests``` folder
4. If there is a error, unable to print uml, then make sure seq.txt and plantuml.jar are in the consistent location as described in line 158 of ```planterUML.py```

```demo.py 

from src.planterUML import Planter

pt = Planter()
pt.prefix = [0, 18, 10, 11] # specify the prefix for which UML will be drawn (has default [0, 18, 10])
# following two lines can be commented out, and then deafult large.msg and sol-sequences.txt will be used (these files can be found in the src folder)
pt.msg_file = 'def.msg' # specify the msg definition file (default is large.msg), best practice is to specify the starting and terminating messages in this file by #
pt.sol_file = 'sol.txt'# specify the solution file
pt.draw(detailed=0) #call the api, detailed = 1 means nodes complete definition, if detailed = 0(which is default), only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.
```

