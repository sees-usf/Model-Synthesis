import java.lang.reflect.InvocationTargetException;

public class Edge {

    private String id;
    private Node source, destination;
    private int support;

    public Edge(Node source, Node destination) {
        this.id = source.toString() + "_" + destination.toString();
        this.source = source;
        this.destination = destination;
        this.support = 0;
    }

    //Copy constructor
    public Edge(Edge edge) throws NoSuchMethodException, SecurityException, InstantiationException,
            IllegalAccessException, IllegalArgumentException, InvocationTargetException, ClassNotFoundException {

        this.id = edge.getId();
        
        this.source = edge.getSource();
        this.destination = edge.getDestination();

        this.support = Integer.valueOf(edge.getEdgeSupport());
    }

    public String getId() {
        return id;
    }

    public Node getSource() {
        return source;
    }

    public Node getDestination() {
        return destination;
    }

    public int getEdgeSupport() {
        return support;
    }

    public void setEdgeSupport(int support) {
        this.support = support;
    }

    public boolean equals(Object obj) {

        if(this == obj)
            return true;
        if(obj == null)
            return false;
        if(getClass() != obj.getClass())
            return false;
        
        Edge other = (Edge) obj;
        
        return id.equals(other.getId());
    
    }
    
}