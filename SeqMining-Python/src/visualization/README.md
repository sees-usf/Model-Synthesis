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
4. If there is a error, unable to print uml, then make sure ```seq{time-st-amp}.txt``` and ```plantuml.jar``` are in the consistent location as described in line 201 of 
```planterUML.py```
5. Enter prefix seperated by spaced only, for example '0 18 10 11' with no ' '.
6. Use no details to caputure large graph, details tends to be cut off.
7. Output files i. a text file, and ii. a png file will be placed in the same folder
