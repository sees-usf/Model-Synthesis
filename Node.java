import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;


public class Node {

    private String symbolIndex, command;
    private ArrayList<Edge> edges;
    private Pair<String, String> message;
    private Node previous;
    private int support, depth, inDegree, outDegree;
    private boolean isVisited;

    public Node(String symbolIndex, Pair<String, String> message, String command) {
        this.symbolIndex = symbolIndex; //Index of stored message
        edges = new ArrayList<Edge>();
        this.support = 0; //Node support
        this.message = message; //Message containing source and destination locations on chip
        this.command = command; //Read or write command stored
        // totalSupport = 0;
        this.depth = 0;
        this.isVisited = false;
        this.depth = 0;
        this.inDegree = 0; //Number of edges incoming
        this.outDegree = 0; //Number of edges outgoing
        this.previous = null;
    }

    //Deep copy constructor
    public Node(Node x) throws NoSuchMethodException, SecurityException, InstantiationException, IllegalAccessException,
            IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        this.symbolIndex = new String(x.symbolIndex);
        this.edges = new ArrayList<Edge>();

        for(Edge edge : x.getEdges()){
            this.edges.add(edge);
        }

        this.previous = x.previous;
        this.support = Integer.valueOf(x.support);
        this.command = new String(x.command);
        this.message = new Pair<>(x.message.getKey(), x.message.getValue());
        //this.totalSupport = x.totalSupport;
        this.depth = Integer.valueOf(x.depth);
        this.isVisited = Boolean.valueOf(x.isVisited);
        this.inDegree = Integer.valueOf(x.inDegree); 
        this.outDegree = Integer.valueOf(x.outDegree); 
    }

    public int getInDegree(){
        return inDegree;
    }

    public int getOutDegree(){
        return outDegree;
    }

    public void setInDegree(int x){
        inDegree = x;
    }

    public void setOutDegree(int x){
        outDegree = x;
    }

    public boolean isVisited(){ 
        return this.isVisited; 
    }

    public void setVisited(boolean isVisited){
        this.isVisited = isVisited;
    }
    
    public int getDepth(){
        return depth;
    }

    public void setDepth(int depth){
        this.depth = depth;
    }

    /*
    public int getTotalSupport(){
        return this.totalSupport;
    }

    public void setTotalSupport(int totalSupport){
        this.totalSupport = totalSupport;
    }
    */

    public int getSupport(){
        return this.support;
    }

    public void setSupport(int support){
        this.support = support;
    }

    public void setSymbolIndex(String symbolIndex){
        this.symbolIndex = symbolIndex;
    }

    public String getSymbolIndex(){
        return this.symbolIndex;
    }

    public Pair<String, String> getMessage(){
        return message;
    }

    public String getCommand(){
        return command;
    }

    public String toString(){
        return this.symbolIndex;
    }

    
    public Node getPrevious(){
        if(this.previous == null)
            return null;
            
        return this.previous;
    }

    public void setPrevious(Node previous){
        this.previous = previous;
    }

    public ArrayList<Edge> getEdges(){
        return this.edges;
    }

    public Edge getEdge(String id){
        for(Edge it : edges)
            if(it.getId().equals(id))
                return it;
        return null;
    }

    public Edge getEdge(Node destination){

        for(Edge edge : edges)
            if(edge.getDestination() == destination)
                return edge;
        
        return null;
    }

    //Edge is added, out degree is updated as well as the in degree of the destination node
    public void addEdge(Edge edge){
        edges.add(edge);
        this.outDegree = this.outDegree + 1;
        edge.getDestination().setInDegree(edge.getDestination().getInDegree()+1);
    }

    //Edge removal, update in degree of destination node and out degree of this node
    public void removeEdge(Edge edge){
        this.outDegree = this.outDegree - 1;
        edge.getDestination().setInDegree(edge.getDestination().getInDegree()-1);
        edges.remove(edge);
    }

    public void removeEdge(Node destination){
        for(Edge it: edges){
            if(it.getDestination() == destination){
                this.outDegree = this.outDegree - 1;
                it.getDestination().setInDegree(it.getDestination().getInDegree()-1);
                edges.remove(it);
                break;
            }
        }
    }

    public void clearEdges(){

        for(Edge it: edges){
            this.outDegree = this.outDegree - 1;
            it.getDestination().setInDegree(it.getDestination().getInDegree()-1);
        }

        edges.clear();
        
    }

    public int getEdgeSupport (Edge edge){
        return edges.get(edges.indexOf(edge)).getEdgeSupport();
    }

    public void setEdgeSupport(Edge edge, int support){
        edges.get(edges.indexOf(edge)).setEdgeSupport(support);
    }

    /*
    public int hashCode() {
        final int prime = 31;
        int result = 1;
        result = prime * result + Integer.valueOf(symbolIndex);
        return result;
    }
    */

    public boolean equals(Object obj) {

        if(this == obj)
            return true;
        if(obj == null)
            return false;
        if(getClass() != obj.getClass())
            return false;
        Node other = (Node) obj;
        if(!symbolIndex.equals(other.getSymbolIndex()))
            return false;
        
        return true;
    }

	public void removeDuplicateEdges() {

        int i = 0;
        while(i < edges.size()){

            Edge it = edges.get(0);
            int timesDetected = 0;
            Edge edge;
            int j = 0;

            while(j < edges.size()){
                edge = edges.get(j);
                if(edge == it){
                    if(timesDetected == 0){
                        timesDetected = timesDetected + 1;
                        continue;
                    }
                    else
                        edges.remove(j);
                }
                j++;
            }

            i++;
        }
	}

}

