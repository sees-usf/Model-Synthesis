import java.util.Comparator;

public class EdgeComparator implements Comparator<Edge> {

    public int compare(Edge lhs, Edge rhs) {

        if(lhs.getEdgeSupport() < rhs.getEdgeSupport()) {
            return 1;
        }

        if(lhs.getEdgeSupport() > rhs.getEdgeSupport()) {
            return -1;
        }

        return 0;
    }

}