import matplotlib.pyplot as plt
import numpy as np

# Sample data
with open("../scenarios/stringStatsFINAL.txt", "r") as f:
    lines = f.readlines()

nodes = []
msgRec = []
msgSent = []
tim = []
errs = []
for line in lines[1:]:
    attr = line.split(",")
    nodes.append(int(attr[0]))
    tim.append(round(float(attr[3]),3))
    msgRec.append(int(attr[4]))
    msgSent.append(int(attr[5]))
    errs.append(int(attr[6]))

print(nodes)
print(msgRec)
print(msgSent)
print(tim)
print(errs)
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

optimum = []
for i in nodes:
    optimum.append(((3*2-1)*i))

ax1.plot(nodes, msgRec, color='green', marker='o', linestyle='-', label="#Request Recieved")
ax1.plot(nodes, msgSent, color='r', marker='o',  linestyle="-", label="#Requests Sent")
ax2.plot(nodes, tim, color="blue", marker='o', linestyle="--", label="Time Taken (s)")
ax1.plot(nodes, optimum, color="#ca19d3", linestyle='-', label="Optimal #Requests", alpha=0.15)

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
plt.savefig('NodesvsReqTime.png')
#plt.show()
