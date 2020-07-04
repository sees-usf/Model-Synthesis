# Sequential Pattern Mining using Data Mining Techniques

**Objectives:** Develop methods and algorithms to mine message flow specifications from execution traces of SoC designs. <br />
This repository reflects the ongoing development of the specification mining algorithm we are working on. We aim for mining a satisfactory number of rules from execution traces which will capture valid sequence of execution for any trigger. There have been many endeavors to determine correct specifications for reactive systems but none of them obliterated the need for further work in this domain. The current advancement in data mining algorithms has also got tremendous interest from specification mining researchers. Many researchers these days are working on the existing data mining algorithms to make them good alternatives to determine an efficient and reliable set of specifications for reactive systems. We also set a goal to utilize state of the art DM techniques to mine specifications in a bigger scale.   

*On-going, more updates will come soon*

**Required Installation:** Please install py4j using "pip install py4j" before running this program.

**Compilation & Instructions:** To run, open Terminal and enter "javac Main.java" then run the program by entering "java Main"

"GatewayServer open, please open a new terminal to run a CSPSolver Python script." should be displayed
and this is when you should open another terminal to run the Python script CSPSolver.py

Once CSPSolver.py is running, information about the program will be displayed as well as instructions on
setting the parameters for limiting the number of solutions to be generated for each trace, as well as whether
the user would like to see each solution for each trace printed to the terminal.

Within the Main.java file, in the Main() function, there are two different definition files and trace files.
"example.def" and "example_trace-1" represents a small example that should generate 16 solutions with OPTIMAL status.

"example_patterns.txt" and "single_no_interleaving.txt" contain a much larger example, solutions will continously print for
a very long time unless a limit is specified by the user.

The solutions will be displayed in the Terminal, if specified. There will be no text file or .pdf generated.

Upon completion of the CSPSolver, to re-run the experiment close all terminals and re-run Main.java and repeat the above instructions.

**Work in Progress:** The generateGraph() function in CSPSolver.py should generate a NetworkX visual representation of each solution upon callback.
However, it is currently implemented in such a way where solutions are unreadable. For this reason, line 29 in CSPSolver.py
has that function call commented out. If you would like to test this function, uncomment line 29 as well as lines 84, 162 and 209 to properly save
the visuals to a pdf file in the current directory called "results.pdf." 
