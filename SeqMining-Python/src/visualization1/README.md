Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. graphviz (for mac: brew install graphviz, for linux: sudo apt install graphviz)
3. plantuml.jar (I have shipped it already or download from: https://plantuml.com/starting)
4. java (should be available in mac, or download from: https://www.java.com/en/download/)
(2,3,4 are plantUML depenencies)

## How to run:
1. Go to visualization directory
2. Go to tests/demo.py
3. Update the syspath to the planterUML.py file of your computer
5. type ``` python3 demo.py sequence-list.txt msg_def.txt```
6. Enter prefix seperated by spaced only, for example '0 18 10 11' with no ' '.
7. Output files i) a text file, and ii)  a .png file will be placed in the same folder
