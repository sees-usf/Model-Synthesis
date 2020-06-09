public class Pair<T,E> {

    private T first;
    private E second;

    public Pair(T first, E second){

        this.first = first;
        this.second = second;
    }

    public T getKey(){
        return first;
    }

    public E getValue(){
        return second;
    }
    
}