import matplotlib.pyplot as plt
# Sample data
with open("../scenarios/stringStats1.csv", "r") as f:
    lines1 = f.readlines()

with open("../scenarios/stringStats2.csv", "r") as f:
    lines2 = f.readlines()

nodes : list[float] = []
msgRec : list[float] = []
msgSent : list[float] = []
tim : list[float] = []
errs : list[float] = []
nodes2 : list[float] = []
msgRec2 : list[float] = []
msgSent2 : list[float] = []
tim2 : list[float] = []
errs2 : list[float] = []

for line in lines1[1:]:
    attr = line.split(",")
    nodes.append(float(attr[0]))
    tim.append(round(float(attr[3]),3))
    msgRec.append(float(attr[4]))
    msgSent.append(float(attr[5]))
    errs.append(float(attr[6]))

for line in lines2[1:]:
    attr = line.split(",")
    nodes2.append(float(attr[0]))
    tim2.append(round(float(attr[3]),3))
    msgRec2.append(float(attr[4]))
    msgSent2.append(float(attr[5]))
    errs2.append(float(attr[6]))

for x in range(len(nodes)):
    nodes[x] = (nodes[x]+nodes2[x])/2
    msgRec[x] = (msgRec[x]+msgRec2[x])/2
    msgSent[x] = (msgSent[x]+msgSent2[x])/2
    tim[x] = (tim[x]+tim2[x])/2
    errs[x] = (errs[x]+errs2[x])/2


print(nodes)
print(msgRec)
print(msgSent)
print(tim)
print(errs)
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

optimum = []
for i in nodes:
    optimum.append(((3*2-1)*i)+i)

ax1.plot(nodes, msgRec, color='green', marker='o', linestyle='-', label="#Request Received")
ax1.plot(nodes, msgSent, color='gray', marker='o',  linestyle="-", label="#Requests Sent")
ax2.plot(nodes, tim, color="blue", marker='o', linestyle="--", label="Time Taken (s)")
ax1.plot(nodes, optimum, color="#ca19d3", linestyle='-', label="Optimal #Requests", alpha=0.2, linewidth=4)
ax1.plot(nodes, errs, color="red", linestyle='--', label="#Errors", alpha=0.2)

ax1.set_xlabel('Number of Nodes')
ax1.set_ylabel('Request Amount')
ax2.set_ylabel('Time Taken (s)', color="blue")


# https://stackoverflow.com/questions/76835526/how-to-add-legend-when-using-twinx
handles_labels = [ax.get_legend_handles_labels() for ax in (ax1, ax2)]
hl_transposed = zip(*handles_labels)
handles, labels = [sum(handles_or_labels, [])
                      for handles_or_labels in hl_transposed]

ax1.legend(handles, labels)


#ax1.legend(loc='upper left')
#ax2.legend(loc='upper left')
#plt.legend(loc='upper left')

plt.xticks(fontsize=14)
plt.yticks(fontsize=13)
plt.grid(True, linestyle=':', alpha=1)

#ax1.set_xscale('log') ;ax1.set_yscale('log') 
#ax2.set_xscale('log') ;ax2.set_yscale('log') 
#plt.xlim(0,150)
#ax1.set_xlim([0,150])
#ax1.set_ylim([0,2500])
#fig.ylim(0,5000)

plt.tight_layout()
#plt.title('Nodes vs Request Amount and Time Taken')
plt.savefig('NodesvsReqTimebefore|.png')
#plt.show()
