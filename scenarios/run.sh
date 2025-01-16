#!/bin/bash

to=$1

for i in $(seq 1 $to); do
  python3 ninrow.py $((2**i))
done

