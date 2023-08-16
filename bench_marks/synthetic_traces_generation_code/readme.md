## Generating Synthetic Traces with Controlled Interleaving

To generate synthetic traces with controlled interleaving among messages of the same flow instance, follow these steps:

1. Create a pattern file (e.g., `pattern.txt`) with the desired message patterns. The pattern file should have a format similar to the following:
   ```plaintext
   0, 25
   0, 8, 12, 25
   0, 8, 12, 13, 15, 23, 24, 25
   0, 8, 12, 13, 46, 47, 24, 25
   # ... (add more patterns)
   ```

2. Open a terminal and execute the following command to generate synthetic traces:
   ```bash
   python scheduler.py --no_of_trace=4 --msg_per_clock=1 --out_file='trace_file.txt' --pattern_per_trace="3,6" --spec_file="small-specs.txt" --threads=2
   ```

   Replace the arguments with your desired parameters:
   - `--no_of_trace`: Number of traces to generate.
   - `--msg_per_clock`: Number of messages per clock cycle.
   - `--out_file`: Output file name for the generated traces.
   - `--pattern_per_trace`: Number of times a pattern appears in each trace.
   - `--spec_file`: Specification file or pattern file.
   - `--threads`: Number of threads to use for parallel processing.

3. The generated traces will be saved in the specified output file (e.g., `trace_file.txt`).

This process allows you to create synthetic traces with specific interleaving patterns among message instances, which can be useful for various testing and analysis purposes.