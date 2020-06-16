import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.Queue;
import java.util.StringTokenizer;

public class Graph {

    private ArrayList<Node> graph; //All nodes in graph
    private ArrayList<Node> roots; //All root nodes
    private ArrayList<Node> termNodes; //All terminal nodes
    private ArrayList<Edge> edges;

    public Graph() {
        graph = new ArrayList<>();
        roots = new ArrayList<>();
        termNodes = new ArrayList<>();
        edges = new ArrayList<>();
    }

    //Copy constructor
    public Graph(Graph graph) throws NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        this.graph = new ArrayList<>();
        this.roots = new ArrayList<>();
        this.termNodes = new ArrayList<>();
        this.edges = new ArrayList<>();

        for (Node it : graph.getNodes()) {

            Node copyNode = new Node(it.getSymbolIndex(), it.getMessage(), it.getCommand());
            copyNode.setSupport(it.getSupport());

            for (Node it2 : graph.getRoots())
                if (it.equals(it2))
                    this.roots.add(copyNode);
            
            for(Node it2 : graph.getTerminalNodes())
                if(it.equals(it2))
                    this.termNodes.add(copyNode);

            this.graph.add(copyNode);
            
        }

        this.generateEdges();

        /*
        for(Node it : this.graph){
            for(Edge it2 : it.getEdges())
                it2.setEdgeSupport(graph.getNode(it.getSymbolIndex()).getEdge(it2.getId()).getEdgeSupport());
        }
        */
    }

    public ArrayList<Node> getRoots() {
        return roots;
    }

    public ArrayList<Node> getTerminalNodes(){
        return termNodes;
    }

    public void addTerminalNode(Node node){
        termNodes.add(node);
    }

    public void addRoot(Node node){
        roots.add(node);
    }

    //Generates dependency graph based on file input
    public void generateGraph(String filename)
            throws IOException, NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        BufferedReader file = new BufferedReader(new FileReader(filename));
        String line;
        ArrayList<String> rootStrings = new ArrayList<>();
        ArrayList<String> termStrings = new ArrayList<>();

        while ((line = file.readLine()) != null) {

            if (line.equals("\n") || line.equals("") || line.contains("Ground"))
                continue;

            StringTokenizer tokenizer = new StringTokenizer(line);

            if(line.contains(",")){ //This if block determines root and terminal nodes
                
                String rootString = tokenizer.nextToken(", ");

                if(!rootStrings.contains(rootString)){
                    
                    rootStrings.add(rootString);

                    String termString = null;

                    while(tokenizer.hasMoreTokens()){
                        termString = tokenizer.nextToken(", ");
                        if(!tokenizer.hasMoreTokens())
                            break;
                    }
                    
                    if(termString != null && !termStrings.contains(termString))
                        termStrings.add(termString);
                }

            }
            else if(line.contains(":")){ //This if block generates nodes with their respective messages and commands

                String token = tokenizer.nextToken(" :");
                String symbolIndex = token;
                token = tokenizer.nextToken(" :");
                String source = token;
                token = tokenizer.nextToken(" :");
                String destination = token;
                token = tokenizer.nextToken(" :");
                String command = token;
    
                Pair<String, String> message = new Pair<>(source, destination);
                Node node;
    
                if ((node = getNode(symbolIndex)) == null) {
                    node = new Node(symbolIndex, message, command);
                    addNode(node);
                    if(rootStrings.contains(symbolIndex)) 
                        roots.add(node);
                    
                    else if(termStrings.contains(symbolIndex))
                        termNodes.add(node);
                    
                }

            }
        }

        file.close();

        generateEdges();
        detectAndRemoveCycle();

    }

    //Generates edges for the dependency graph
    private void generateEdges() {
        for(Node it: graph){

            if(termNodes.contains(it))
                continue;

            Pair<String,String> message = it.getMessage();

            for(Node it2: graph){
                if(it == it2 || isRoot(it2))
                    continue;

                if(message.getValue().equals(it2.getMessage().getKey())){
                    Edge edge = new Edge(it, it2);
                    it.addEdge(edge);
                    edges.add(edge);
                }
            }
        }
    }

    //Removes cycles from dependency graph
    private void detectAndRemoveCycle() throws NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        ArrayList<Node> recStack = new ArrayList<>();
        resetVisitedNodes();
        Graph copy = new Graph(this);

        for(Node node : graph)
            DFSUtil(copy.getNode(node.getSymbolIndex()), recStack);

    }

    public void DFSUtil(Node node, ArrayList<Node> recStack){

        if(!node.isVisited()){

            node.setVisited(true);
            recStack.add(node);

            for(Edge edge : node.getEdges()){

                Node destination = edge.getDestination();

                if(!destination.isVisited())
                {
                    if(getEdge(edge.getSource().getSymbolIndex(), edge.getDestination().getSymbolIndex()) == null)
                        continue;
                                
                    DFSUtil(destination, recStack);
                }
                else if(recStack.contains(destination))
                    removeEdge(edge.getSource().getSymbolIndex(), edge.getDestination().getSymbolIndex());
                                
            }
        }

        recStack.remove(node);
    }

    public ArrayList<Graph> generateDAGS() throws NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        ArrayList<Graph> dags = new ArrayList<>();
        Queue<Node> traversal = new LinkedList<>();
        //ArrayList<Queue<Node>> traversals = new ArrayList<>();

        for(Node root : roots){
            resetVisitedNodes();
            Graph dag = new Graph();
            traversal.add(root);
            DAGUtil(dag, traversal);
            dags.add(dag);
        }

        return dags;
    }

    private void DAGUtil(Graph dag, Queue<Node> queue)
            throws NoSuchMethodException, SecurityException, InstantiationException, IllegalAccessException,
            IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        if (queue.isEmpty())
            return;
        
        Node v = queue.poll();
        Node copy = new Node(v);

        if(roots.contains(v)){
            v.setVisited(true);
            dag.addRoot(copy);
            dag.addNode(copy);
        }

        for(Edge edge : v.getEdges()){
            if(!edge.getDestination().isVisited()){
                Node u = edge.getDestination();
                u.setVisited(true);
                dag.addNode(new Node(u));
                queue.add(u);
            }
        }

        if(v.getEdges().isEmpty())
            dag.addTerminalNode(copy);

        DAGUtil(dag, queue);

    }

    public boolean hasNode(Node u) {
        return graph.contains(u);
    }

    public boolean hasNode(String u){
        for(Node node : graph)
            if(u.equals(node.getSymbolIndex()))
                return true;

        return false;
    }


    private boolean isRoot(Node node) {
        for(Node root: roots)
            if(root == node)
                return true;

        return false;
    }

    public void addNode(Node node) {
        graph.add(node);
    }

    public Node getNode(String id){
        for(Node it : graph)
            if(id.equals(it.getSymbolIndex()))
                return it;
        return null;
    }

    public ArrayList<Node> getNodes(){
        return graph;
    }

    public void removeNode(Node node){

        if(!graph.contains(node)){
            System.out.println("Node not in graph.\n");
            return;
        }

        for(Node it: graph) {

            if(it == node)
                continue;
            
            it.removeEdge(node);
        }

        for(Node it: graph){

            if(it == node)
                continue;

            node.removeEdge(it);
            
        }

        graph.remove(node);
    }

    public void removeNode(String node){

        Node temp = null;

        for(Node it: graph) 
            if(it.getSymbolIndex().equals(node))
                temp = it;

        if(temp != null)
            removeNode(temp);
        
    }

    public void addEdge(Node origin, Edge edge){

        origin.addEdge(edge);
        
    }

    public void addEdge(String origin, String destination){

        for(Node it : graph){
            
            if(it.getSymbolIndex().equals(origin)) {
                
                for(Node it2 : graph){
                    if(it2.getSymbolIndex().equals(destination)){
                        it.addEdge(new Edge(it, it2));
                        break;
                    }
                }

                break;
            }
        }  
    }

    public void removeEdge(Node origin, Node destination){

        if(!graph.contains(origin)){
            System.out.println("Origin not in graph.\n");
            return;
        }
        
        if(!graph.contains(destination)){
            System.out.println("Destination not in graph.\n");
            return;
        }

        Edge edge = origin.getEdge(destination);
        edges.remove(edge);
        origin.removeEdge(edge);

    }

    public void removeEdge(String origin, String destination){

        for(Node it : graph){ 
            if(it.getSymbolIndex().equals(origin)) {
                for(Node it2 : graph){
                    if(it2.getSymbolIndex().equals(destination)){
                        Edge edge = it.getEdge(it2);
                        edges.remove(edge);
                        it.removeEdge(edge);
                        return;
                    }
                }
            }
        }

        System.out.println("Edge not found in graph.\n");

    }
    public Edge getEdge(String origin, String destination){

        for(Node it : graph){ 
            if(it.getSymbolIndex().equals(origin)) {
                for(Edge edge : it.getEdges()){
                    if(edge.getDestination().getSymbolIndex().equals(destination)){
                        return edge;
                    }
                }
            }
        }

        System.out.println("Edge not found in graph.\n");
        return null;

    }

    public void removeEdge(Node origin, Edge edge){
        edges.remove(edge);
        origin.removeEdge(edge);
    }

    public void printGraph(){
        printNodes();
        printEdges();
    }

    public void printEdges() {

        for(Node it : graph){

            if(it == null)
                break;

            System.out.print("Origin: " + it.getSymbolIndex() + ": " 
                            + it.getMessage().getKey() + " to "
                            + it.getMessage().getValue() + " "
                            + "\nEdges:\n");
            
                            
            //System.out.println("Origin: " + it.getSymbolIndex());
            for(Edge it2 : it.getEdges()){
                System.out.println(it2.getId() + " with edge support of " + it2.getEdgeSupport());
            }
            
            System.out.println("");
        
        }

    }

    public void printNodes() {

        System.out.print("Nodes: \n");
        int totalSupport = 0;
        for(Node it: graph){
            System.out.println(it.getSymbolIndex() + " " + it.getMessage().getKey()
                                + " to " + it.getMessage().getValue()
                                + " with support of " + it.getSupport()
                                + " and in degree of " + it.getInDegree()
                                + " and out degree of " + it.getOutDegree()
                                + " while visited = " + it.isVisited());
            totalSupport += it.getSupport();
        }
        System.out.println("Total Support: " + totalSupport);
    }
    
    public void resetVisitedNodes(){
        for(Node it: graph)
            it.setVisited(false);
    }

    public void resetNodeSupport(){
        for(Node it : graph)
            it.setSupport(0);

    }

    public void resetEdgeSupport(){
        for(Node node: graph)
            for(Edge edge : node.getEdges())
                edge.setEdgeSupport(0);

    }

    public void resetGraphSupport(){
        for(Node node : graph){
            node.setSupport(0);
            for(Edge edge : node.getEdges())
                edge.setEdgeSupport(0);
        }
    }
}