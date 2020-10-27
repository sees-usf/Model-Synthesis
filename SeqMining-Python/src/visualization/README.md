Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. graphviz (for mac: brew install graphviz, for linux: sudo apt install graphviz)
3. plantuml.jar (I have shipped it already or download from: https://plantuml.com/starting)
4. java (should be available in mac, or download from: https://www.java.com/en/download/)
(2,3,4 are plantUML depenencies)

How to run:
A simple example is given in demo.py script

```
#demo.py
from src.planterUML import Planter

pt = Planter()
pt.prefix = [0, 18, 10, 11] # specify the prefix for which UML will be drawn (has default [0, 18, 10])
#following two lines can be commented out, and then deafult 'large.msg' and 'sol-sequences.txt' will be used (these files can be found in the src folder)
pt.msg_file = './tests/def.msg' # specify the msg definition file (default is large.msg)
pt.sol_file = './tests/sol.txt'# specify the solution file (defualt is 'sol-sequences.txt')
pt.draw(detailed=0) #call the api, detailed = 1 means nodes complete definition, if detailed = 0(which is default), only number in the sequences will be there. The purpose is to prevent UMLs from being cut off.
```

## Tips:
1. Import Planter in a script that is in a folder(say tests) in the same directory as src
2. Use detailed = 0 for better visual
3. If the error is unable to draw, make sure seq.txt and plantuml.jar are placed correctly as they are called in line 158 in planterUML.py
4. Put no blank newline at the end of your sequence file



