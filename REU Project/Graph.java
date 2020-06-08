import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.StringTokenizer;

public class Graph {

    private ArrayList<Node> graph; //All nodes in graph
    private ArrayList<Node> roots; //All root nodes
    private ArrayList<Node> termNodes; //All terminal nodes

    public Graph() {
        graph = new ArrayList<>();
        roots = new ArrayList<>();
        termNodes = new ArrayList<>();
    }

    //Copy constructor
    public Graph(Graph graph) throws NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        this.graph = new ArrayList<>();
        this.roots = new ArrayList<>();
        this.termNodes = new ArrayList<>();

        for (Node it : graph.getNodes()) {

            Node copyNode = new Node(it.getSymbolIndex(), it.getMessage(), it.getCommand());
            copyNode.setSupport(it.getSupport());

            for (Node it2 : graph.getRoots())
                if (it == it2)
                    this.roots.add(copyNode);
            
            for(Node it2 : graph.getTerminalNodes())
                if(it == it2)
                    this.termNodes.add(copyNode);

            this.graph.add(copyNode);
            
        }

        this.generateEdges();

        for(Node it : this.graph){

            for(Edge it2 : it.getEdges())
                it2.setEdgeSupport(graph.getNode(it.getSymbolIndex()).getEdge(it2.getId()).getEdgeSupport());
        }
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

        if(graph.contains(node))
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
                    it.addEdge(new Edge(it, it2));
                }
            }
        }
    }

    //Removes cycles from dependency graph
    private void detectAndRemoveCycle() {

        Queue<Node> queue = new LinkedList<>(); //Queue for BFS traversal
        List<Edge> edgesToBeRemoved = new LinkedList<>(); //List edges to be removed
        List<List<Node>> traversals = new LinkedList<>(); //List of traversal path

        for(Node node : graph){

            //If node has not been visited yet, conduct BFS traversal
            if(!node.isVisited()){
                List<Node> traversal = new LinkedList<>();
                node.setVisited(true);
                queue.add(node);
                traversal.add(node);
                BFSUtil(node, queue, edgesToBeRemoved, traversal);
                //System.out.println();
                traversals.add(traversal);
            }
        }

        //For every traversal, check to see if the node at the end of the traversal
        //cycles back to the beginning node of the traversal and remove that edge
        for(List<Node> traversal : traversals){
            Node v = traversal.get(traversal.size()-1);
            for(Edge edge : v.getEdges())
                if(edge.getDestination() == traversal.get(0))
                    edgesToBeRemoved.add(edge);
        }


        for(Edge edge : edgesToBeRemoved)
            removeEdge(edge.getSource(), edge);

    }

    public ArrayList<Graph> generateDAGS(){

        ArrayList<Graph> dags = new ArrayList<>();
        Queue<Node> queue = new LinkedList<>();

        for(Node root : roots){
            
            resetVisitedNodes();
            Graph dag = new Graph();
            queue.add(root);
            DAGUtil(dag, queue);
            dag.generateEdges();
            dags.add(dag);
        }

        return dags;
    }

    private void DAGUtil(Graph dag, Queue<Node> queue) {

        if (queue.isEmpty())
            return;
        
        Node v = queue.poll();
        Node copy = new Node(v.getSymbolIndex(), v.getMessage(), v.getCommand());

        if(roots.contains(v)){
            v.setVisited(true);
            dag.addRoot(copy);
            dag.addNode(copy);
        }

        for(Edge edge : v.getEdges()){
            if(!edge.getDestination().isVisited()){
                Node u = edge.getDestination();
                u.setVisited(true);
                dag.addNode(new Node(u.getSymbolIndex(), u.getMessage(), u.getCommand()));
                queue.add(u);
            }
        }

        if(v.getEdges().isEmpty())
            dag.addTerminalNode(copy);

        DAGUtil(dag, queue);

    }

    // BFS Graph traversal to detect cycles
    public void BFSUtil(Node start, Queue<Node> queue, List<Edge> edgesToBeRemoved, List<Node> traversal) {

        if(queue.isEmpty())
            return;
        
        Node v = queue.poll();

        //System.out.print(v.getSymbolIndex() + " ");
        traversal.add(v);

        for(Edge edge : v.getEdges()){
            if(!edge.getDestination().isVisited()){
                edge.getDestination().setVisited(true);
                edge.getDestination().setPrevious(v);
                queue.add(edge.getDestination());
            }
            else if(edge.getDestination() == v.getPrevious()) //|| queue.contains(edge.getDestination())) //if edge leads to cycle, add to list for removal
                edgesToBeRemoved.add(edge);
        }

        BFSUtil(start, queue, edgesToBeRemoved, traversal); //Recursive call
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

        origin.removeEdge(destination);

    }

    public void removeEdge(String origin, String destination){

        for(Node it : graph){ 
            if(it.getSymbolIndex().equals(origin)) {
                for(Node it2 : graph){
                    if(it2.getSymbolIndex().equals(destination)){
                        it.removeEdge(it2);
                        return;
                    }
                }
            }
        }

        System.out.println("Edge not found in graph.\n");

    }

    public void removeEdge(Node origin, Edge edge){
        origin.removeEdge(edge);
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