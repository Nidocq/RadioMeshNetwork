#!/bin/bash

to=$1

for i in $(seq $to); do
  python3 ninrow.py $((2**$i))

done

