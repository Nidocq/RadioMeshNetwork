import matplotlib.pyplot as plt
# Sample data
#fileName = "reliableReport20.csv"
#fileName = "reliableReport50.csv"
#fileName = "reliableReport200.csv"
#fileName = "reliabilityResultsFLOOD20.txt"
#fileName = "reliabilityResultsFLOOD50.txt"
fileName = "reliableReport2212FLOODING.csv"
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
for line in lines[1:]:
    attr = line.split(",")
    nodes.append(int(attr[0]))
    messages.append(int(attr[1]))
    hopLimit.append(int(attr[2]))
    msgSent.append(int(attr[3]))
    msgRec.append(int(attr[4]))
    errs.append(int(attr[5]))
    route_recv.append(int(attr[9]))

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

#optimum = []
#for i in nodes:
#    optimum.append(((3*2-1)*i))

ax1.plot(hopLimit, errs, color="red", linestyle='-', label="#Errors", alpha=0.3)
ax1.plot(hopLimit, route_recv, color="green", linestyle='-', label="#Route requests received")
ax2.plot(hopLimit, msgRec, color='green', linestyle='--', label="#Request Received", alpha=0.4)
ax2.plot(hopLimit, msgSent, color='blue', linestyle="--", label="#Requests Sent", alpha=0.4)
#plt.plot(hopLimit, nodes, color="blue", marker='o', linestyle="--", label="nodes")
#plt.plot(hopLimit, messages, color="yellow", marker='o', linestyle="--", label="")
#plt.plot(nodes, route_recv, color="pink", linestyle='-', label="(nodes) route_recv")

ax1.set_xlabel('Hop Limit')
ax2.set_ylabel('#Requests')
#plt.xlabel("Hop Limit")
#plt.ylabel("#Messages")

# https://stackoverflow.com/questions/76835526/how-to-add-legend-when-using-twinx
handles_labels = [ax.get_legend_handles_labels() for ax in (ax1, ax2)]
hl_transposed = zip(*handles_labels)
handles, labels = [sum(handles_or_labels, [])
                      for handles_or_labels in hl_transposed]

ax1.legend(handles, labels)
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

#plt.legend(loc='upper left')

#plt.xticks(fontsize=14)
#plt.yticks(fontsize=13)
plt.grid(True, linestyle=':', alpha=1)

#ax1.set_xscale('log') ;ax1.set_yscale('log') 
#ax2.set_xscale('log') ;ax2.set_yscale('log') 
#plt.xlim(0,150)
#ax1.set_xlim([0,150])
#ax1.set_ylim([0,2500])
#fig.ylim(0,5000)

plt.tight_layout()
#plt.title('Hop Limit with Nodes & 400 messages')
#plt.savefig('reliabilityNetwork|||.png')
plt.savefig(f'reliability{fileName}twinxFixReceiveRedacted.png')
#plt.show()
