import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.Scanner;
import java.util.Stack;

import py4j.GatewayServer;

public class Main {

    private Graph graph = null;
    private Stack<String> traces = null;
    private String traceFileName, defFileName;

    public static void main(String[] args) throws IOException, NoSuchMethodException, SecurityException,
            InstantiationException, IllegalAccessException, IllegalArgumentException, InvocationTargetException,
            ClassNotFoundException {

        GatewayServer gatewayServer = new GatewayServer(new Main());
        gatewayServer.start();
        System.out.println("GatewayServer open, please open a new terminal to run a CSPSolver Python script.");

        
        //String string = System.getProperty("os.name").toLowerCase();
        
        /*
        if(string.contains("windows")){
            try
            { 
                // Just one line and you are done !  
                // We have given a command to start cmd 
                // /K : Carries out command specified by string 
            Runtime.getRuntime().exec("cmd /c start cmd.exe /K \"py CSPSolver.py\""); 
    
            } 
            catch (Exception e) 
            { 
                System.out.println("Cannot open cmd prompt"); 
                e.printStackTrace(); 
            } 
        }
        */

    }

    //Below are a list of functions that can be called within any Python script
    //that connects to the GatewayServer of this process

    //Main function called by py4j GatewayServer
    //Generates the graph and a stack of traces

    public Main() throws IOException, NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {
        
        graph = new Graph();
        
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter definition filename: ");
        defFileName = scanner.nextLine();
        //defFileName = "example.def";
        //defFileName = "example_patterns.txt";
        
        System.out.print("Enter trace filename: ");
        traceFileName = scanner.nextLine();
        //traceFileName = "example_trace-1";
        //traceFileName = "single_no_interleaving_trace_1.txt";
        
        scanner.close();
        
        graph.generateGraph(defFileName);
        generateTraces(traceFileName);
        
        /*
        for(Graph dag : graph.generateDAGS()){
            System.out.println("-----------------------------------------------");
            dag.printEdges();
            System.out.println("-----------------------------------------------");

        }
        */
    }

    public String getTraceFileName(){
        return traceFileName;
    }

    public String getDefFileName(){
        return defFileName;
    }

    //Returns Graph object
    public Graph getGraph() {
        return graph;
    }

    public Boolean hasTraces(){
        if(traces.isEmpty())
            return false;
        return true;
    }

    //Prepares traces
    public void generateTraces(String filename) throws IOException {
        BufferedReader fileReader = new BufferedReader(new FileReader(filename));
        traces = new Stack<>();

        while(fileReader.ready()){
            String trace = fileReader.readLine();

            if(trace.equals("\n") || trace.equals(""))
                continue;
            
            traces.add(trace);
            
        }

        fileReader.close();
    }

    //Pops a trace from the stack and annotates the graph passed
    public void annotateGraph() throws IOException {
        PatternDetector pd = new PatternDetector(traces.pop(), graph);
        pd.beginAnnotation();
    }
}