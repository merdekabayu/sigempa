#! /bin/sh

SIZE="M14c"
AXIS="a4f2/a4f2nwse"
psfile="fungsi/gmt/sensor_status.ps"
REGION=124/129/-2.75/3.0
gmt set FONT_ANNOT_PRIMARY 11p

#echo %evlon% %evlat% > %parameter%
gmt grdimage fungsi/gmt/indo.nc -R$REGION -J$SIZE -Cfungsi/gmt/full_white.cpt -Sn -Q -K -V -I+a0+nt0.5 -Y3.5 > $psfile
gmt pscoast -Dh -R -J -W0.6,0 -K -O -V >> $psfile


gmt psbasemap -J -R -B$AXIS  --MAP_LABEL_OFFSET=0.1 --FONT_LABEL=17p,Heveltica --MAP_FRAME_TYPE=plain --FONT_ANNOT=16p -K -O -V >> $psfile
awk '{print $1-0.2, $2+0.15, TR, $4}' fungsi/gmt/status.dat | gmt pstext -J -R -F+f9.5,17,red -Gwhite -O -K >> $psfile

gmt psxy fungsi/gmt/status.dat -J -R -O -K -St0.3i -Cfungsi/gmt/status.cpt -W0 >> $psfile

gmt pstext -R -J -O -K -V -F+f11,17,0 <<EOF>> $psfile
127.4 -2.6 last updated: $1 $2 UTC
EOF

gmt pslegend fungsi/gmt/sensor.txt -R -J -F+gwhite+p -Dx4.65i/0.1i/2i/1.8i/TC -C0.15i/0.05i -O -Y15.5 -X-9 >> $psfile


gmt psconvert $psfile -Tj -A -P

#cp fungsi/gmt/sensor_status.jpg static/sensor_status.jpg