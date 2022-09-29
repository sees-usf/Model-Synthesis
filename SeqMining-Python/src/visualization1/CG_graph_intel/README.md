Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. pygraphviz (for linux: ```pip3 install pygraphviz```)


## How to run:
1. Open compactUML.py
2. Go to line 447
3. Specify the prefix as a python list
4. Specify the message definition file, the content of the file should be same format as in large.msg
5. Specify the sequences file. the content of the file should be same format as in sol-sequences.txt
6. type ``` python3 compactUML.py```
7. Generated graphs will be placed in the diagrams folder
8. Dot notation and selected seqences will be presented on the cmd
9. compactUML.py can export ```Planter``` class. In that can use regular python module import strategy and comment out line 446 to 450 