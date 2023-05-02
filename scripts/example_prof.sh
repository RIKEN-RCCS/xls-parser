#!/usr/bin/bash

OUTDIR=xls_out
mkdir -p ${OUTDIR}

for i in $(seq 1 17); do
  fapp -C -d tmp/rep${i} -Icpupa -Hevent=pa${i} ./main
  fapp -A -d tmp/rep${i} -Icpupa -txml -o ${OUTDIR}/pa${i}.xml
done
