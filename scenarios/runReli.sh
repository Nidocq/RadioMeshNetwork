
#!/bin/bash

to=$1

for i in $(seq 3 3 $to); do
  #python3 reliability.py 50 60000 60600 6 100 $i 1 0 50 for the hop limit 50 nodes 100 messages test
  python3 reliability.py $i 60000 60600 6 100 $i 1 0 50
done


