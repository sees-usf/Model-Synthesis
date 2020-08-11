import java.util.LinkedList;
import java.util.Queue;
import java.util.StringTokenizer;

public class PatternDetector {

    private Graph graph, dag;
    private String trace;
    private String originalTrace;


    //Tokenizes string input, generates trace for graph annotation
    public PatternDetector(String originalTrace, Graph graph) {

        this.graph = graph;
        this.originalTrace = originalTrace;
        trace = "";

    }

    public PatternDetector(String originalTrace, Graph dag, Graph graph) {

        this.graph = graph;
        this.dag = dag;
        this.originalTrace = originalTrace;
        trace = "";

    }

    public void beginDAGAnnotation(){

        StringTokenizer tokenizer = new StringTokenizer(originalTrace);
        while(tokenizer.hasMoreTokens()) {

            String token = tokenizer.nextToken(" ");

            if(token.equals("-2"))
                break;
            
            if(dag.getNode(token) == null || token.equals("-1")) 
                continue;

            //temp
            dag.getNode(token).setSupport(dag.getNode(token).getSupport() + 1);
            
            trace += token + " ";

        }

        for(Edge edge: dag.getEdges())
            annotateDAGEdge(edge);
        
        dag.resetVisitedNodes();

    }

    //Need to account for different roots, which edge pertains which root. Some dags have same edges, but different roots
    //Still needs work, remember DAGS do not have cyclic edges removed
    public void annotateDAGEdge(Edge edge){
        
        Queue<String> rootQueue = new LinkedList<String>();
        int sourceInstances = 0;
        StringTokenizer tokenizer = new StringTokenizer(trace);
        String sourceSymbolIndex = edge.getSource().getSymbolIndex();
        String rootSymbolIndex = dag.getRoots().get(0).getSymbolIndex(); //root node ID

        while(tokenizer.hasMoreTokens()) 
        {
            String token = tokenizer.nextToken(" ");
            
            if(graph.isRoot(token))
            {
                rootQueue.add(token);
                if(token.equals(sourceSymbolIndex))
                    sourceInstances++;
            }
            else if(token.equals(sourceSymbolIndex))
                sourceInstances++;
            else if(edge.getId().equals(sourceSymbolIndex+"_"+token) && sourceInstances > 0 && !rootQueue.isEmpty())
            {
                String root = rootQueue.poll();

                if(root.equals(rootSymbolIndex))
                {
                    edge.setEdgeSupport(edge.getEdgeSupport() + 1);
                    //if(!edge.getDestination().isVisited())
                    //    edge.getDestination().setSupport(edge.getDestination().getSupport() + 1);
                }

                sourceInstances--;
            }   
        }

        if(!edge.getDestination().isVisited())
            edge.getDestination().setVisited(true);
    }

    //Annotate every edge in graph
    public void beginAnnotation() {
        
        StringTokenizer tokenizer = new StringTokenizer(originalTrace);
        
        while(tokenizer.hasMoreTokens()) {

            String token = tokenizer.nextToken(" ");

            if(token.equals("-2"))
                break;
            
            if(graph.getNode(token) == null || token.equals("-1")) //Increments node support by one if a node is detected
                continue;
            
            graph.getNode(token).setSupport(graph.getNode(token).getSupport() + 1);

            trace += token + " ";

        }

        for(Node it : graph.getNodes()) 
            if(!it.getEdges().isEmpty())   
                for(Edge it2: it.getEdges())
                    annotateEdge(it2);   
                   
    }

    //Edge annotation
    private void annotateEdge(Edge edge) {

        int instances = 0; //Keeps track of active instances of source nodes detected
        StringTokenizer tokenizer = new StringTokenizer(trace);
        String symbolIndex = edge.getSource().getSymbolIndex(); //Source node ID

        while(tokenizer.hasMoreTokens()) {

            String token = tokenizer.nextToken(" ");

            if(!token.equals("-1")){
                if(symbolIndex.equals(token)) //Create instance if token is equal to source ID
                    instances++;
                else if (edge.getId().equals(symbolIndex + "_" + token) && instances > 0){ //If destination is detected, increment edge support and decrement one instance
                    edge.setEdgeSupport(edge.getEdgeSupport()+1);
                    instances--;
                }
            }

        }
    }
}