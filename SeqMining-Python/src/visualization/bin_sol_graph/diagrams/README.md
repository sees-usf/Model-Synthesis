Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. pygraphviz (for linux: ```pip3 install pygraphviz```)


## How to run:
1. Open draw_graph.py
2. Go to line 266
3. Specify the message definition file, the content of the file should be same format as in ```large.msg```
4. Specify the solution file. the content of the file should be same format as in ```model.txt```
5. From cmd of the same folder, type ``` python3 draw_graph.py```
6. Generated graphs will be placed in the diagrams folder
8. Dot notation and selected seqences will be presented on the cmd
9. draw_graph.py can export ```Planter``` class. In that can use regular python module import strategy and comment out line 266 to 267 