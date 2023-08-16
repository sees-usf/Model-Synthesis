# Coded By Bardia Nadimi
# Feb 2023
# University of South Florida

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *
from gem5.runtime import get_runtime_isa

# Add the common scripts to our path
m5.util.addToPath("../libraries/")

# import the caches which we made
from caches import *

# import the SimpleOpts module
from common import SimpleOpts

# Default to running 'hello', use the compiled ISA to find the binary
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
default_binary = os.path.join(
    thispath,
    "../libraries/",
    "test-progs/threads/bin/x86/linux/threads",
    # "test-progs/hello/bin/x86/linux/pat",
    # "test-progs/hello/bin/x86/linux/hello",
)
second_binary = os.path.join(
    thispath,
    "../libraries/",
    # "tests/test-progs/threads/bin/x86/linux/threads",
    "test-progs/hello/bin/x86/linux/hello",
)

# Binary to execute
SimpleOpts.add_option("binary", nargs="?", default=default_binary)
SimpleOpts.add_option("binary1", nargs="?", default=second_binary)

# Finalize the arguments and grab the args so we can pass it on to our objects
args = SimpleOpts.parse_args()

# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("32GB")]  # Create an address range

# Create a simple cpu0 and cpu1
system.cpu0 = X86TimingSimpleCPU()
system.cpu1 = X86TimingSimpleCPU()
system.cpu2 = X86TimingSimpleCPU()
system.cpu3 = X86TimingSimpleCPU()

# Create an L1 instruction and data cache
system.cpu0.icache = L1ICache(args)
system.cpu0.dcache = L1DCache(args)
# Create an L1 instruction and data cache
system.cpu1.icache = L1ICache(args)
system.cpu1.dcache = L1DCache(args)
# Create an L1 instruction and data cache
system.cpu2.icache = L1ICache(args)
system.cpu2.dcache = L1DCache(args)
# Create an L1 instruction and data cache
system.cpu3.icache = L1ICache(args)
system.cpu3.dcache = L1DCache(args)

# Comm Monitors between cpu0 and icache, dcache
system.cpu0_icache0 = CommMonitor()
system.cpu0_icache0.cpu_side_port = system.cpu0.icache_port
system.cpu0_dcache0 = CommMonitor()
system.cpu0_dcache0.cpu_side_port = system.cpu0.dcache_port
# Comm Monitors between cpu1 and icache, dcache
system.cpu1_icache1 = CommMonitor()
system.cpu1_icache1.cpu_side_port = system.cpu1.icache_port
system.cpu1_dcache1 = CommMonitor()
system.cpu1_dcache1.cpu_side_port = system.cpu1.dcache_port
# Comm Monitors between cpu1 and icache, dcache
system.cpu2_icache2 = CommMonitor()
system.cpu2_icache2.cpu_side_port = system.cpu2.icache_port
system.cpu2_dcache2 = CommMonitor()
system.cpu2_dcache2.cpu_side_port = system.cpu2.dcache_port
# Comm Monitors between cpu1 and icache, dcache
system.cpu3_icache3 = CommMonitor()
system.cpu3_icache3.cpu_side_port = system.cpu3.icache_port
system.cpu3_dcache3 = CommMonitor()
system.cpu3_dcache3.cpu_side_port = system.cpu3.dcache_port

# Connect the instruction and data caches to the cpu0
system.cpu0.icache.cpu_side = system.cpu0_icache0.mem_side_port 
system.cpu0.dcache.cpu_side = system.cpu0_dcache0.mem_side_port 
# Connect the instruction and data caches to the cpu1
system.cpu1.icache.cpu_side = system.cpu1_icache1.mem_side_port 
system.cpu1.dcache.cpu_side = system.cpu1_dcache1.mem_side_port 
# Connect the instruction and data caches to the cpu1
system.cpu2.icache.cpu_side = system.cpu2_icache2.mem_side_port 
system.cpu2.dcache.cpu_side = system.cpu2_dcache2.mem_side_port 
# Connect the instruction and data caches to the cpu1
system.cpu3.icache.cpu_side = system.cpu3_icache3.mem_side_port 
system.cpu3.dcache.cpu_side = system.cpu3_dcache3.mem_side_port 

# Create a memory bus, a coherent crossbar, in this case
system.l2bus = L2XBar()

system.l2bus_l2cache = CommMonitor()
system.l2bus_l2cache.cpu_side_port = system.l2bus.mem_side_ports 

system.icache0_l2bus = CommMonitor()
system.icache0_l2bus.cpu_side_port = system.cpu0.icache.mem_side
system.dcache0_l2bus = CommMonitor()
system.dcache0_l2bus.cpu_side_port = system.cpu0.dcache.mem_side

system.icache1_l2bus = CommMonitor()
system.icache1_l2bus.cpu_side_port = system.cpu1.icache.mem_side
system.dcache1_l2bus = CommMonitor()
system.dcache1_l2bus.cpu_side_port = system.cpu1.dcache.mem_side

system.icache2_l2bus = CommMonitor()
system.icache2_l2bus.cpu_side_port = system.cpu2.icache.mem_side
system.dcache2_l2bus = CommMonitor()
system.dcache2_l2bus.cpu_side_port = system.cpu2.dcache.mem_side

system.icache3_l2bus = CommMonitor()
system.icache3_l2bus.cpu_side_port = system.cpu3.icache.mem_side
system.dcache3_l2bus = CommMonitor()
system.dcache3_l2bus.cpu_side_port = system.cpu3.dcache.mem_side

# Hook the cpu0 ports up to the l2bus
system.icache0_l2bus.mem_side_port = system.l2bus.cpu_side_ports
system.dcache0_l2bus.mem_side_port = system.l2bus.cpu_side_ports

system.icache1_l2bus.mem_side_port = system.l2bus.cpu_side_ports
system.dcache1_l2bus.mem_side_port = system.l2bus.cpu_side_ports

system.icache2_l2bus.mem_side_port = system.l2bus.cpu_side_ports
system.dcache2_l2bus.mem_side_port = system.l2bus.cpu_side_ports

system.icache3_l2bus.mem_side_port = system.l2bus.cpu_side_ports
system.dcache3_l2bus.mem_side_port = system.l2bus.cpu_side_ports

# Create an L2 cache and connect it to the l2bus
system.l2cache = L2Cache(args)
system.l2cache.cpu_side = system.l2bus_l2cache.mem_side_port

system.l2cache_membus = CommMonitor()
system.l2cache_membus.cpu_side_port = system.l2cache.mem_side

# Create a memory bus
system.membus = SystemXBar()

system.membus_dram = CommMonitor()
system.membus_dram.cpu_side_port = system.membus.mem_side_ports

# Connect the L2 cache to the membus
system.l2cache_membus.mem_side_port = system.membus.cpu_side_ports 

# create the interrupt controller for the cpu0
system.cpu0.createInterruptController()
system.cpu0.interrupts[0].pio = system.membus.mem_side_ports
system.cpu0.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu0.interrupts[0].int_responder = system.membus.mem_side_ports
# create the interrupt controller for the cpu1
system.cpu1.createInterruptController()
system.cpu1.interrupts[0].pio = system.membus.mem_side_ports
system.cpu1.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu1.interrupts[0].int_responder = system.membus.mem_side_ports
# create the interrupt controller for the cpu2
system.cpu2.createInterruptController()
system.cpu2.interrupts[0].pio = system.membus.mem_side_ports
system.cpu2.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu2.interrupts[0].int_responder = system.membus.mem_side_ports
# create the interrupt controller for the cpu3
system.cpu3.createInterruptController()
system.cpu3.interrupts[0].pio = system.membus.mem_side_ports
system.cpu3.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu3.interrupts[0].int_responder = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a DDR3 memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR4_2400_16x4() #DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0] #AddrRange('32GB') 
system.mem_ctrl.port = system.membus_dram.mem_side_port

system.workload = SEWorkload.init_compatible(args.binary)

# Create a process for a simple "Hello World" application
# process = Process()
process0 = Process(pid=100)
# process1 = Process(pid=101)
# Set the command
# cmd is a list which begins with the executable (like argv)
# process.cmd = [args.binary]
process0.cmd = [args.binary]
# process1.cmd = [args.binary1]
# Set the cpu0 to use the process as its workload and create thread contexts
# system.cpu0.workload = process
# system.cpu1.workload = process
system.cpu0.workload = process0
system.cpu0.createThreads()
system.cpu1.workload = process0
system.cpu1.createThreads()
system.cpu2.workload = process0
system.cpu2.createThreads()
system.cpu3.workload = process0
system.cpu3.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))
