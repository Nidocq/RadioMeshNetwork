import matplotlib.pyplot as plt
# Sample data
#fileName = "reliableReport20.csv"
#fileName = "reliableReport50.csv"
#fileName = "reliableReport200.csv"
#fileName = "reliabilityResultsFLOOD20.txt"
#fileName = "reliabilityResultsFLOOD50.txt"
#fileName = "reliableReport2212FLOODING.csv"
#fileName = "reliability_0301_RANDOM_WALK_NodesVariable.txt"
#fileName = "averaged_data.csv"
#fileNames = ["reliability_0301_RANDOM_WALK_NodesVariable.txt", 
#fileNames = ["reliability_1101_RANDOM_WALK_HopLimit_50N100M4.txt", "reliability_1101_RANDOM_WALK_HopLimit_50N100M3.txt", "reliability_1101_RANDOM_WALK_HopLimit_50N100M2.txt", "reliability_1101_RANDOM_WALK_HopLimit_50N100M1.txt", "reliability_1101_RANDOM_WALK_HopLimit_50N100M.txt"]
fileName = "averaged_varNodeLinear.csv"
#reliability_1101_RANDOM_WALK_NodesVar_linear.txt
with open(f"../scenarios/{fileName}", "r") as f:
    lines = f.readlines()

#1 nodes
#2 messages
#3 hop limit
#4 messages sent 
#5 messages recv
#6 errors
#7 route recv
nodes = []
messages = []
hopLimit= []
msgSent = []
msgRec = []
errs = []
route_recv= []
route_recv_perc = []
errors_to_msg_perc = []
for line in lines[1:]:
    attr = line.split(",")
    nodes.append(float(attr[0]))
    messages.append(float(attr[1]))
    hopLimit.append(float(attr[2]))
    msgSent.append(float(attr[3]))
    msgRec.append(float(attr[4]))
    errs.append(float(attr[5]))
    route_recv.append(float(attr[8]))
    if float(attr[3]) == 0:
        route_recv_perc.append(0)
    else:
        route_recv_perc.append((float(attr[8])/float(attr[3]))*100)
    if float(attr[5]) == 0:
        errors_to_msg_perc.append(0)
    else:
        errors_to_msg_perc.append((float(attr[5])/float(attr[3]))*100)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

#optimum = []
#for i in nodes:
#    optimum.append(((3*2-1)*i))
#ax1.plot(hopLimit, errs, color="red", linestyle='-', label="#Errors", alpha=0.3)
ax1.plot(nodes, route_recv, color="green", linestyle='-', label="#Route requests received")
#ax2.plotnodest, msgRec, color='green', linestyle='--', label="#Request Received", alpha=0.4)
ax2.plot(nodes, route_recv_perc, color='blue', linestyle="--", label="% Requests recieve to total requests sent", alpha=0.4, linewidth=2.5)
ax2.plot(nodes, errors_to_msg_perc, color='red', linestyle="--", label="% Requests sent to errors", alpha=0.4)
#plt.plot(hopLimit, nodes, color="blue", marker='o', linestyle="--", label="nodes")
#plt.plot(hopLimit, messages, color="yellow", marker='o', linestyle="--", label="")
#plt.plot(nodes, route_recv, color="pink", linestyle='-', label="(nodes) route_recv")

ax1.set_xlabel('Number of Nodes')
ax1.set_ylabel('Route Requests Received')
ax2.set_ylabel('Percentage (%)')
#plt.xlabel("Hop Limit")
#plt.ylabel("#Messages")

# https://stackoverflow.com/questions/76835526/how-to-add-legend-when-using-twinx
handles_labels = [ax.get_legend_handles_labels() for ax in (ax1, ax2)]
hl_transposed = zip(*handles_labels)
handles, labels = [sum(handles_or_labels, [])
                      for handles_or_labels in hl_transposed]

fontsize = 8
ax1.legend(handles, labels, fontsize=fontsize)
ax1.legend(loc='upper left', fontsize=fontsize)
ax2.legend(loc='upper right', fontsize=fontsize)

#plt.legend(loc='upper left')

#plt.xticks(fontsize=14)
#plt.yticks(fontsize=13)
plt.grid(True, linestyle=':', alpha=1)

#ax1.set_xscale('log') ;ax1.set_yscale('log') 
#ax2.set_xscale('log') ;ax2.set_yscale('log') 
#plt.xlim(0,150)
#ax1.set_xlim([0,150])
ax1.set_ylim([0,186])
#ax2.set_ylim([0,30])
#fig.ylim(0,5000)

plt.tight_layout()
#plt.title('Hop Limit with Nodes & 400 messages')
#plt.savefig('reliabilityNetwork|||.png')
plt.savefig(f'NodeVar{fileName}.png')
#plt.show()
