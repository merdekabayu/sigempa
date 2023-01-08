#!/bin/bash
export SEISCOMP_ROOT="/home/sysop/seiscomp"
export PATH="/home/sysop/seiscomp/bin:/home/sysop/bin:$PATH"
export LD_LIBRARY_PATH="/home/sysop/seiscomp/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="/home/sysop/seiscomp/lib/python:$PYTHONPATH"
export MANPATH="/home/sysop/seiscomp/share/man:$MANPATH"
cat /home/sysop/seiscomp/var/lib/archive/2023/*/*/*/*.005 /home/sysop/seiscomp/var/lib/archive/2023/*/*/*/*.006|scmssort -v -t '2023-01-05 23:50:00~2023-01-06 00:10:00' -u > '/home/sysop/vps_server/waveform.mseed'