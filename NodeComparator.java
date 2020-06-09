import java.util.Comparator;

public class NodeComparator implements Comparator<Node> {

    public int compare(Node lhs, Node rhs) {

        if(lhs.getSupport() > rhs.getSupport()) {
            return 1;
        }

        if(lhs.getSupport() < rhs.getSupport()) {
            return -1;
        }

        return 0;
    }

}