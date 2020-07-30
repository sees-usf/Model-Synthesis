import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.Scanner;
import java.util.Stack;

import py4j.GatewayServer;

public class Main {

    private Graph graph = null;
    private Stack<String> traces = null;
    private String traceFileName, defFileName;
    private ArrayList<Graph> dags;

    public static void main(String[] args)
            throws IOException, NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        GatewayServer gatewayServer = new GatewayServer(new Main());
        gatewayServer.start();
        Boolean isWindows = System.getProperty("os.name").toLowerCase().startsWith("windows");

        if (isWindows)
            //Runtime.getRuntime().exec("cmd /c start cmd.exe /K \"py CSPSolver.py\"");
            Runtime.getRuntime().exec("cmd /c start cmd.exe /K \"python Z3Solver.py\"");
        else {
            Process process = Runtime.getRuntime().exec("python3 cspsolver.py");
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null)
                System.out.println(line);
            reader.close();
        }
        
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
        //defFileName = scanner.nextLine();
        defFileName = "example.def";
        //defFileName = "example_patterns.txt";
        
        System.out.print("Enter trace filename: ");
        //traceFileName = scanner.nextLine();
        traceFileName = "example_trace-1";
        //traceFileName = "trace1.txt";
        
        scanner.close();
        
        graph.generateGraph(defFileName);
        generateTraces(traceFileName);

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

    public void popTrace(){
        traces.pop();
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
        PatternDetector pd = new PatternDetector(traces.peek(), graph);
        pd.beginAnnotation();
    }

    public ArrayList<Graph> getAnnotatedDAGS() throws NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        dags = graph.generateDAGS();

        for(Graph dag : dags){
            PatternDetector pd = new PatternDetector(traces.peek(), dag, graph);
            pd.beginDAGAnnotation();
            dag.printGraph();
        }

        return dags;

    }
}