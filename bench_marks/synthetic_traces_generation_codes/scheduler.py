import threading
import random
import time
import numpy as np
import argparse
import warnings

pattern_db = {}
uniq_msgs = []
# out_file = ""

# args
# out_file=out_file, pattern_freq_per_trace="3", max_msg_per_clock=1, no_of_trace=3, detailed_trace="N", no_of_threads=4, t=dist

def get_args():
    parser = argparse.ArgumentParser("args")
    sim_args(parser)
    parser.set_defaults(embedding="AngleEmbedding")
    return parser.parse_args()


def sim_args(parser):
    parser = parser.add_argument_group("sim")
    parser.add_argument("--msg_per_clock", default=1, type=int, help="Maximum msg per clock")
    parser.add_argument("--no_of_trace", default="1", type=int, help="Number of traces to be produced")
    parser.add_argument(
        "--detailed", default="N", type=str, help="Specify if the address information will be in the traces"
    )
    parser.add_argument("--threads", default=2, type=int, help="number of threads(cpu)")
    parser.add_argument("--dist", default=10, type=int, help="maximum distance between two msgs from the same flow instance")
    parser.add_argument(
        "--pattern_per_trace", default="3,5", type=str, help="Specify number of times each pattern will be present in the trace."
    )
    parser.add_argument("--out_file", default="test_trace.txt", type=str, help="Generated trace file.")
    parser.add_argument("--spec_file", default="small-specs.txt", type=str, help="Input spec file.")

def detailed_tracer(patterns):
    address_patterns = []
    for pattern in patterns:
        temp = []
        number = random.randrange(1023, 1087) # mem address range, should be same in both detailed_tracer() and reiterate() methods
        for event in pattern:
            temp.append((event,number))
        address_patterns.append(temp)
    return address_patterns

def check_db():  #checks if there is any element left for printing, accessing each iterator and checking if there is something left to call
    if (pattern_db) == 0:
        return False
    
    for i in pattern_db:
        if pattern_db[i][1]>0:
            return True
    else:
        return False

class SharedResourceScheduler:
    def __init__(self, num_consumers, max_access_event, patterns, consumers):
        self.num_consumers = num_consumers
        self.no_access_count = [0] * num_consumers
        self.max_access_event = max_access_event
        self.patterns = patterns
        self.consumers = consumers

    def acquire_resource(self, consumer_id):    
        if max(self.no_access_count) >= self.max_access_event:
            priority_id = self.no_access_count.index(max(self.no_access_count))
            for i in range(len(self.no_access_count)):
                if i != priority_id:
                    self.no_access_count[i] += 1
                self.no_access_count[priority_id] = 0
        else:
            priority_id = consumer_id
            for i in range(len(self.no_access_count)):
                if i != priority_id:
                    self.no_access_count[i] += 1
                self.no_access_count[priority_id] = 0

        # print(self.consumers, " Priority id: ", priority_id, " ",consumer_id)
        ev = next(self.patterns[priority_id], None)

        if ev == None:
            # print(self.consumers," removed: ", priority_id)
            self.consumers.remove(priority_id)
            self.no_access_count[priority_id] = -100000
            return ev, priority_id
        else:
            # print(priority_id, end=" ")
            # print(ev[0], end=" -1 ")
            # out_file.write(str(ev[0])+" -1 ")
            return ev, priority_id
    

def simulate(patterns="",t=20, out_file=""):
        N = len(patterns)
        consumers = []

        for i in range(N):
            consumers.append(i)

        if t<N: #interval between last msg seen must be greater than or equal to the number of CPUs.
            print("Interval t between last msg seen must be greater than or equal to the number of CPUs.\n Forcing t = #CPU*2 for simulation.")
            t = N*2

        scheduler = SharedResourceScheduler(N, t, patterns, consumers)

        while True:
            if len(consumers) == 0:
                break
            else:
                consumer_id = random.choice(consumers)
                ev, id = scheduler.acquire_resource(consumer_id)

                if ev:
                    out_file.write(str(ev[0])+" -1 ")
                    # print(ev[0], end=" -1 ")          


def tracer(no_of_threads,out_file, t):
    while(check_db()):
        activate_threads = random.randint(1,  no_of_threads)
        pat_indices =  pattern_db.keys()
        
        if len(pat_indices) < activate_threads:
            activate_threads = len(pat_indices)

        active_pats = random.sample(pat_indices, activate_threads)
        threads = []

        for i in active_pats:
            threads.append(iter(pattern_db[i][0]))
            pattern_db[i][1] = pattern_db[i][1] -1
            if pattern_db[i][1] == 0:
                del pattern_db[i]
                # print("deleted", i)
        print("Active_pattern(s)",active_pats, " on ", len(active_pats), " CPU(s)")
        
        # print(threads)
        simulate(threads, t=t, out_file=out_file)
        print("\n")
    
    print()


def run_tracer(patterns, out_file, pattern_freq_per_trace, max_msg_per_clock, no_of_trace, detailed_trace, no_of_threads, t):
    cnt  = 0
    global pattern_db

    while cnt < no_of_trace:
        patterns_ = detailed_tracer(patterns)
        # print(patterns_)
        random.shuffle(patterns_)
        
        for i, pat in enumerate(patterns_):
            if "," in pattern_freq_per_trace:
                a,b = pattern_freq_per_trace.split(",")
                no_repeats  = random.randint(int(a),int(b))
            else:
                no_repeats = int(pattern_freq_per_trace)
            pattern_db[i] = [pat, no_repeats]
        tracer(no_of_threads,out_file,t)
        # for i in pattern_db:
        #     print(pattern_db[i])
        cnt +=1
        out_file.write(" -2\n")

def get_patterns(file):
    global uniq_msgs
    patterns = []
    with open(file, "r", encoding='utf-8-sig') as f:
        lines = [line.strip() for line in f.readlines()]
        for line in lines:
            temp = (line.split(","))
            temp =[int(i) for i in temp]
            patterns.append(temp)
            uniq_msgs.extend(temp)
    uniq_msgs = set(uniq_msgs)
    print(uniq_msgs, len(uniq_msgs))
    return patterns


# main script
def main():
    warnings.filterwarnings("ignore")
    # os.makedirs("resource", exist_ok=True)
    # global   out_file
    # out_file = open('test_trace.txt', "w")

    # detailed='N', dist=10, embedding='AngleEmbedding', msg_per_clock=1, no_of_trace=1, out_file='test_trace.txt', pattern_per_trace='3,5', spec_file='small-specs.txt', threads=2

    args = get_args()
    out_file = open(args.out_file, "w")
    patterns = get_patterns(args.spec_file)

    run_tracer(patterns, out_file=out_file, pattern_freq_per_trace=args.pattern_per_trace, max_msg_per_clock=args.msg_per_clock, no_of_trace=args.no_of_trace, detailed_trace=args.detailed, no_of_threads=args.threads, t=args.dist)

    out_file.close()

    # uniq_msgs = set(uniq_msgs)
    # print(f'Unique messages: {uniq_msgs},\nTotal: {len(uniq_msgs)}')

if __name__ == "__main__":
    main()