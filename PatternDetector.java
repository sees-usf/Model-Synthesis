import java.util.StringTokenizer;

public class PatternDetector {

    private Graph graph;
    private String trace;


    //Tokenizes string input, generates trace for graph annotation
    public PatternDetector(String originalTrace, Graph graph) {

        this.graph = graph;
        
        StringTokenizer tokenizer = new StringTokenizer(originalTrace);
        trace = "";

        while(tokenizer.hasMoreTokens()) {

            String token = tokenizer.nextToken(" ");

            if(token.equals("-2"))
                break;
            
            if(graph.getNode(token) == null || token.equals("-1")) //Increments node support by one if a node is detected
                continue;
            
            graph.getNode(token).setSupport(graph.getNode(token).getSupport() + 1);

            trace += token + " ";

        }
    }

    public void beginDAGAnnotation(){

        for(Node it : graph.getNodes()) 
            if(!it.getEdges().isEmpty())   
                for(Edge it2: it.getEdges())
                    annotateDAGEdge(it2);  

    }

    public void annotateDAGEdge(Edge edge){

        int rootInstances = 0, sourceInstances = 0; //Keeps track of active instances of source nodes detected
        StringTokenizer tokenizer = new StringTokenizer(trace);
        String sourceSymbolIndex = edge.getSource().getSymbolIndex();
        String rootSymbolIndex = graph.getRoots().get(0).getSymbolIndex(); //Source node ID

        while(tokenizer.hasMoreTokens()) {

            String token = tokenizer.nextToken(" ");

            if(!token.equals("-1")){
                if(token.equals(rootSymbolIndex)){ //Create instance if token is equal to source ID
                    rootInstances++;
                    if(rootSymbolIndex.equals(sourceSymbolIndex))
                        sourceInstances++;
                }
                else if(token.equals(sourceSymbolIndex))
                    sourceInstances++;
                else if (edge.getId().equals(sourceSymbolIndex + "_" + token) && rootInstances > 0 && sourceInstances > 0){ //If destination is detected, increment edge support and decrement one instance
                    edge.setEdgeSupport(edge.getEdgeSupport()+1);
                    rootInstances--;
                    sourceInstances--;
                }
            }
        }

    }

    //Annotate every edge in graph
    public void beginAnnotation() {

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
                else if (edge.getId().equals(symbolIndex + "_" + token) && instances != 0){ //If destination is detected, increment edge support and decrement one instance
                    edge.setEdgeSupport(edge.getEdgeSupport()+1);
                    instances--;
                }
            }

        }
    }
}