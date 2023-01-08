#!/bin/bash
pwd
export SEISCOMP_ROOT="/home/sysop/seiscomp"
export PATH="/home/sysop/seiscomp/bin:/home/sysop/bin:$PATH"
export LD_LIBRARY_PATH="/home/sysop/seiscomp/lib:$LD_LIBRARY_PATH"
export PYTHONPATH="/home/sysop/seiscomp/lib/python:$PYTHONPATH"
export MANPATH="/home/sysop/seiscomp/share/man:$MANPATH"
cat /home/sysop/seiscomp/var/lib/archive/2023/IA/TNTI/*Z*/*.006 /home/sysop/seiscomp/var/lib/archive/2023/IA/TNTI/*Z*/*.007|scmssort -v -t '2023-01-06 17:41:56~2023-01-07 17:41:56' -u >'/home/sysop/vps_server/TNTI.mseed'