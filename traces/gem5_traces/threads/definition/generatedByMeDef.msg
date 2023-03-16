#
0  : cpu0:icache0:read:req
10 : cpu0:dcache0:write:req
14 : cpu0:dcache0:read:req
24 : cpu1:icache1:read:req
28 : cpu1:dcache1:write:req
32 : cpu1:dcache1:read:req
#
1 : l2bus:l2cache:read:req
2 : icache0:l2bus:read:req
3 : membus:dram:read:req
4 : l2cache:membus:read:req
5 : dram:membus:read:resp
6 : membus:l2cache:read:resp
7 : l2cache:l2bus:read:resp
8 : l2bus:icache0:read:resp
11 : dcache0:l2bus:read:req
12 : l2bus:dcache0:read:resp
16 : l2bus:l2cache:read/write:req
17 : icache0:l2bus:read/write:req
18 : dcache0:l2bus:read/write:req
19 : l2bus:l2cache:write:req
20 : dcache0:l2bus:write:req
21 : l2cache:membus:read/write:req
22 : membus:dram:write:req
23 : l2cache:membus:write:req
25 : icache1:l2bus:read:req
26 : l2bus:icache1:read:resp
29 : dcache1:l2bus:read:req
30 : l2bus:dcache1:read:resp
34 : dcache1:l2bus:read/write:req
35 : l2bus:dcache1:read/write:resp
36 : l2cache:l2bus:read/write:resp
37 : icache1:l2bus:read/write:req
38 : l2bus:dcache0:read/write:resp
39 : dcache1:l2bus:write:req
40 : membus:l2cache:read/write:resp
#
9  : icache0:cpu0:read:resp
13 : dcache0:cpu0:write:resp
15 : dcache0:cpu0:read:resp
27 : icache1:cpu1:read:resp
31 : dcache1:cpu1:write:resp
33 : dcache1:cpu1:read:resp
#