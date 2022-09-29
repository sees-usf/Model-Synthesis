## Dependencies:
1. python 3.x (should be available by default in all unix/linux systems)
2. pygraphviz (for linux: ```pip3 install pygraphviz```)
3. graphviz (could be installed with ```apt``` for ubuntu, ```brew``` for mac)


## How to run/import:
1. Planter class can be imported as shown in ```demo.py```
2. Call ```draw()``` with two arguments as following:
    1. Specify the message definition file, the content of the file should be same format as in ```large.msg```
    2. Specify the solution file. the content of the file should be same format as in ```model.txt```
3. Generated graphs will be placed in the ```diagrams``` folder
4. You can change the output directory change the ```file_str``` in the ```draw_graph.py``` file