## Generating Traces with Gem5 Architectural Simulator

The used Gem5 traces are not uploaded in this repository due to the size issues, however, all of the configuration files used for generating Gem5 traces can be found in this repository. To regenerate the Gem5 traces follow the below instructions:

1. Install the Gem5 Artichetural simulator. (instructions on installing can be found at: https://www.gem5.org/getting_started/)

2. The "FS" folder includes configuration and other needed files for full system mode and the "SE" folder includes configuration and other needed files for syscall emulation mode. Copy these folders into the "gem5" directory.

3. For generating "threads" Gem5 traces run the following command:
   ```
   build/X86/gem5.opt --debug-flags=CommMonitor --debug-file=trace.txt.gz <path to gem5 directory>/SE/threads/threads_config.py
   ```

4. For generating "snoop" Gem5 traces run the following command:
   ```
   build/X86/gem5.opt --debug-flags=CommMonitor --debug-file=trace.txt.gz <path to gem5 directory>/SE/snoop/snoop_config.py
   ```

5. For generating "kernel" Gem5 traces run the following command:

   ```
   build/X86/gem5.opt --debug-flags=CommMonitor --debug-file=trace.txt.gz <path to gem5 directory>/FS/full_system/full_system.py --kernel <path to gem5 directory>/MyResources/vmlinux-4.4.186 --disk-image <path to gem5 directory>/MyResources/x86-ubuntu-generatedImage -n 2
   ```
remember to replace <path to gem5 directiry> with the actual path where you installed the Gem5 simulator.