#!/usr/bin/bash

OUTDIR=output
mkdir -p ${OUTDIR}
for i in $(seq 1 17); do
  fapppx -A -d tmp/rep${i} -Icpupa -tcsv -o ${OUTDIR}/pa${i}.csv
done
cp $(dirname $(which fccpx))/../misc/cpupa/cpu_pa_report.xlsm ${OUTDIR}
# rm -rf tmp
zip -r dummy-fapp-profile.zip ${OUTDIR}
