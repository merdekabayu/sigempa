#! /bin/sh

SIZE="M17.2c"
AXIS="a2f1NwsE"
namafile = $9
psfile="fungsi/gmt/$9.ps"
evlat=$1
evlon=$2
magfile=$3
skala=$4
kiri=$5
kanan=$6
bawah=$7
atas=$8
REGION=$kiri/$kanan/$bawah/$atas
kota_besar_malut="fungsi/gmt/kota_besar_malut.dat"
kota_malut="fungsi/gmt/kota_malut.dat"
kota_sulut="fungsi/gmt/kota_sulutgto.dat"
parameter="fungsi/gmt/parameter.dat"
magnitudo="fungsi/gmt/mag/$magfile"

#echo %evlon% %evlat% > %parameter%
grdimage fungsi/gmt/indo.nc -R$REGION -J$SIZE -Cfungsi/gmt/batimetri.cpt -K -V -I+a0+nt0.5 -Y8 -P > $psfile
psxy -R -JM -W1.0 -Sf0.4i/0.05ilt -Gblack -O -K  fungsi/gmt/trench.gmt>> $psfile

echo $evlon $evlat | psxy -R -JM -O -K -Sa0.2i -Wthin,red -Gred>> $psfile
echo $evlon $evlat | psxy -R -JM -O -K -Sc0.3i -W2,red >> $psfile
echo $evlon $evlat | psxy -R -JM -O -K -Sc0.6i -W2,red >> $psfile
echo $evlon $evlat | psxy -R -JM -O -K -Sc0.9i -W2,red >> $psfile
psxy $kota_malut -R -JM -O -K -Sc0.1i -G0 >> $psfile
psxy $kota_sulut -R -JM -O -K -Sc0.1i -G0 >> $psfile
psxy $kota_besar_malut -R -JM -O -K -Ss0.17i -W3,red >> $psfile
awk '{ print $1+0.08,$2,$3,$4,$5,$6,$7}' $kota_besar_malut | pstext -R -JM -O -K >> $psfile
awk '{ print $1+0.06,$2,$3-4,$4,$5,$6,$7}' $kota_malut | pstext -R -JM -O -K >> $psfile
awk '{ print $1+0.06,$2,$3-4,$4,$5,$6,$7}' $kota_sulut | pstext -R -JM -O -K >> $psfile
#awk '{print $1+0.12, $2, BL, $14}' tahun_focal.txt |

psbasemap -J -R$REGION -B$AXIS --MAP_LABEL_OFFSET=0.2 --FONT_ANNOT_PRIMARY=9p --FONT_LABEL=11p,Heveltica --MAP_FRAME_TYPE=inside --MAP_FRAME_WIDTH=0.1p -P -K -O -V -Lf$skala/1/100+lKM  >> $psfile

pscoast -Dl -R111/141/-10/7 -JM3.5c -W0.3,gray40 -Swhite -Ggray40 --MAP_FRAME_TYPE=inside -O -K -V -Blrbt -Y0.1 -X1.1>> $psfile

psxy -J -R -W1,red -O -K <<EOF>> $psfile
$kiri $atas
$kiri $bawah
$kanan $bawah
$kanan $atas
$kiri $atas
EOF

echo $evlon $evlat | psxy -R -J -O -K -Sa0.2c -Gred >> $psfile
psimage fungsi/gmt/template_peta0.png -Dx0/0+w7.5i+r300 -O -X-2 -Y-6.7 -K>> $psfile
psimage $magnitudo -Dx0/0+w1.6i+r600 -O -X1.55 -Y2 -K>> $psfile
awk '{ print $1,$2,$3}' fungsi/gmt/param.txt | pstext -R1/10/1/10 -JX3 -F+cTL+f11,Times-Bold,white -P -O -K -Y-0.35 -X6>> $psfile
awk '{ print $4,$5}' fungsi/gmt/param.txt | pstext -R1/10/1/10 -JX3 -F+cTL+f11,Times-Bold,white  -P -O -K -Y-0.45 >> $psfile
awk '{ print $6,$7,$8,$9,$10}' fungsi/gmt/param.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f11,Times-Bold,white  -P -O -Y-3.7 -K -X-0.05 >> $psfile
awk '{ print $11,$12}' fungsi/gmt/param.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f11,Times-Bold,white  -P -O -K -Y-0.1 -X6 >> $psfile
awk '{ print $1,$2,$3,$4}' fungsi/gmt/jarak.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f10,Times-Bold,white  -P -O -K -Y2.25 >> $psfile
awk '{ print $13}' fungsi/gmt/param.txt | pstext -R1/20/1/10 -JX5 -F+cTL+f10,Times-Bold,white  -P -O -Y-0.43>> $psfile
psconvert $psfile -TG -A -P -E256

echo "Halo disini nilai R = $R"
pwd

#lat=$1
#long=$2
#mag=$3
#psfile="/home/operasional/flask_app/fungsi/testing.ps"
#pscoast -JM15 -R120/130/-5/5 -Gdarkgreen -Swhite -Dh -Ba2f2 -K> $psfile
#echo $long $lat | psxy -R120/130/-5/5 -J -Sc0.5c -Gred -O >> $psfile
#echo "Ini Magnitude file $mag"
#psconvert -A -Tg $psfile
cp fungsi/gmt/$9.png static/map-detail/$9.png