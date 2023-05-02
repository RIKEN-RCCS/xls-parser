#!/usr/bin/bash
#PJM -L node=1
#PJM -L elapse=0:10:00

make main

mkdir -p tmp

for i in $(seq 1 17); do
  fapp -C -d tmp/rep${i} -Icpupa -Hevent=pa${i} ./main
done
