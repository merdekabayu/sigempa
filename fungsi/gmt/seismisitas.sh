#! /bin/sh

SIZE="M16c"
AXIS="a2f1/a2f1NWse"
psfile="fungsi/gmt/seismisitas_mingguan.ps"
start=$1
end=$2
gempa="fungsi/gmt/gempa_mingguan.txt"
dirasakan="fungsi/gmt/dirasakan_mingguan.txt"
REGION=124/130/-2.75/3.5


#echo %evlon% %evlat% > %parameter%
grdimage fungsi/gmt/indo.nc -R$REGION -J$SIZE -Cfungsi/gmt/batimetri.cpt -Sn -Q -K -V -I+a0+nt0.5 -Y3.5 > $psfile
pscoast -Dh -R -J -W0.6,gray30 -K -O -V >> $psfile
psxy -R -J -W1.5 -Sf0.4i/0.06ilt -Gblack -m -O -K fungsi/gmt/trench.gmt >> $psfile

awk '{print $1, $2, $3, $4*0.035}' $gempa | psxy -J -R -Sci -Cfungsi/gmt/depth.cpt -W0.5 -O  -K -V >> $psfile
awk '{print $1, $2, $3}' $dirasakan | psxy -J -R -Sa0.25i -Gred -W1 -O  -K -V >> $psfile

psbasemap -J -R -B$AXIS -Lf124.7/3.1/0/100+lkm  --MAP_LABEL_OFFSET=0.1 --FONT_LABEL=17p,Heveltica --MAP_FRAME_TYPE=fancy --FONT_ANNOT=16p -K -O -V >> $psfile
pstext -R -J -O -K -V <<EOF>> $psfile
129.9 2.8 45 90 34  BL \343
129.8 2.55 20 0 1 BR N
EOF



psxy fungsi/gmt/kota-halmahera.txt -J -R -O -K -Sc0.06i -G0 >> $psfile
psxy fungsi/gmt/kota-prop.txt -J -R -O -K -Ss0.08i -G0 >> $psfile
awk '{print $1-0.1, $2+0.08, BR, $4}' fungsi/gmt/kota-halmahera.txt | pstext -J -R -F+f10,Times-Bold,black -O -K >> $psfile
awk '{print $1-0.15, $2+0.08, BR, $4}' fungsi/gmt/kota-prop.txt | pstext -J -R -F+f12,Times-Bold,black -O -K >> $psfile

pslegend fungsi/gmt/legenda_1.txt -R -J -F+gwhite+p -Dx4.75i/0.25i/7.5i/0.95i/TC -C0.1i/0.1i -O -K -Y-1.5 -X-4 >> $psfile

pscoast -Dl -R94/143/-12/12 -JM5 -Ba237wnse -Wthinnest -Swhite -Ggray40 -O -K -V -X14.9 -Y1.6 --MAP_FRAME_TYPE=plain  >> $psfile

psxy -J -R -W3,red -O -V <<EOF>> $psfile
124 3.5
130 3.5
130 -2.75
124 -2.75
124 3.5
EOF


psconvert $psfile -Tj -A -P

cp fungsi/gmt/seismisitas_mingguan.jpg static/seismisitas_mingguan.jpg