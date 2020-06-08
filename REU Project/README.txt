Required Installation:

Please install py4j using "pip install py4j" before running this program.

Compilation & Instructions:

To run, open Terminal and enter "javac Main.java" then run the program by entering "java Main"

"GatewayServer open, please open a new terminal to run a CSPSolver Python script." should be displayed
and this is when you should open another terminal to run the Python script CSPSolver.py

Once CSPSolver.py is running, information about the program will be displayed as well as instructions on
setting the parameters for limiting the number of solutions to be generated for each trace, as well as whether
the user would like to see each solution for each trace printed to the terminal.

Within the Main.java file, in the Main() function, there are two different definition files and trace files.
"example.def" and "example_trace-1" represents a small example that should generate 16 solutions with OPTIMAL status.

"example_patterns.txt" and "single_no_interleaving.txt" contain a much larger example, solutions will continously print for
a very long time unless a limit is specified by the user.

Currently, the smaller example is the default. If you'd like to run the larger example, uncomment lines 61 and 64 in Main.java and comment out
the other example filenames.

The solutions will be displayed in the Terminal, if specified. There will be no text file or .pdf generated.

Upon completion of the CSPSolver, to re-run the experiment close all terminals and re-run Main.java and repeat the above instructions.

Work in Progress:

The generateGraph() function in CSPSolver.py should generate a NetworkX visual representation of each solution upon callback.
However, it is currently implemented in such a way where solutions are unreadable. For this reason, line 29 in CSPSolver.py
has that function call commented out. If you would like to test this function, uncomment line 29 as well as lines 84, 162 and 209 to properly save
the visuals to a pdf file in the current directory called "results.pdf." 



        


